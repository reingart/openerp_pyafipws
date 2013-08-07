#!/usr/bin/python
# -*- coding: utf-8 -*-
# This program is free software; you can redistribute it and/or modify
# it under the terms of the Affero GNU General Public License as published by
# the Software Foundation; either version 3, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTIBILITY
# or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
# for more details.
#
# Copyright 2013 by Mariano Reingart
# Based on code "factura_electronica" by Luis Falcon 
# Based on code "openerp-iva-argentina" by Gerardo Allende / Daniel Blanco
# Based on code "l10n_ar_wsafip_fe" by OpenERP - Team de Localización Argentina

"Electronic Invoice for Argentina Federal Tax Administration (AFIP) webservices"

__author__ = "Mariano Reingart (reingart@gmail.com)"
__copyright__ = "Copyright (C) 2013 Mariano Reingart and others"
__license__ = "AGPL 3.0+"


from osv import fields, osv
import os, time
import datetime
import decimal
import os
import socket
import sys
import traceback

DEBUG = True


class electronic_invoice(osv.osv):
    _name = "account.invoice"
    _inherit = "account.invoice"
    _order = "id"
    _columns = {
        'pyafipws_concept': fields.selection([
                        ('1','1-Productos'),
                        ('2','2-Servicios'),
                        ('3','3-Productos y Servicios'),
                        ], 'Concepto', select=True, required=True),
        'pyafipws_billing_start_date': fields.date('Inicio período facturado',
            help="Seleccionar fecha de fin de servicios - Sólo servicios"),
        'pyafipws_billing_end_date': fields.date('Fin del período facturado',
            help="Seleccionar fecha de inicio de servicios - Sólo servicios"),
        'pyafipws_result': fields.selection([
                ('', 'n/a'),
                ('A', 'Aceptado'),
                ('R', 'Rechazado'),
                ('O', 'Observado'),
            ], 'Resultado', size=1, readonly=True,
            help="Resultado procesamiento de la Solicitud, devuelto por AFIP"),
        'pyafipws_cae': fields.char('CAE', size=14, readonly=True,
            help="Código de Autorización Electrónico, devuelto por AFIP"),
        'pyafipws_cae_due_date': fields.date('Vencimiento CAE', readonly=True,
            help="Fecha tope para verificar CAE, devuelto por AFIP"),
        'pyafipws_message': fields.text('Mensaje', readonly=True,
            help="Mensaje de error u observación, devuelto por AFIP"),
        'pyafipws_xml_request': fields.text('Requerimiento XML', readonly=True,
            help="Mensaje XML enviado a AFIP (depuración)"),
        'pyafipws_xml_response': fields.text('Respuesta XML', readonly=True,
            help="Mensaje XML recibido de AFIP (depuración)"),
        'pyafipws_barcode': fields.char('Codigo de Barras', size=40,),
    }
    _defaults = {
         'pyafipws_concept': lambda *a: '1',
    }

    def do_pyafipws_request_cae(self, cr, uid, ids, *args):
        for invoice in self.browse(cr, uid, ids):
            # if already authorized (electronic invoice with CAE), ignore
            if invoice.pyafipws_cae:
                continue
            # get the electronic invoice type, point of sale and service:
            journal = invoice.journal_id
            company = journal.company_id
            tipo_cbte = journal.pyafipws_invoice_type
            punto_vta = journal.pyafipws_point_of_sale
            service = journal.pyafipws_electronic_invoice_service
            # check if it is an electronic invoice sale point:
            if not tipo_cbte or not punto_vta or not service:
                continue
            # authenticate against AFIP:
            auth_data = company.pyafipws_authenticate(service=service)            
            # import AFIP webservice helper for electronic invoice
            from pyafipws.wsfev1 import WSFEv1
            wsfev1 = WSFEv1()
            # connect to the webservice and call to the test method
            wsfev1.Conectar()
            # set AFIP webservice credentials:
            wsfev1.Cuit = company.pyafipws_cuit
            wsfev1.Token = auth_data['token']
            wsfev1.Sign = auth_data['sign']

            # get the last 8 digit of the invoice number
            cbte_nro = invoice.number[-8:]
            # get the last invoice number registered in AFIP
            cbte_nro_afip = wsfev1.CompUltimoAutorizado(tipo_cbte, punto_vta)
            cbte_nro_next = int(cbte_nro_afip or 0) + 1
            # verify that the invoice is the next one to be registered in AFIP    
            if False and cbte_nro != cbte_nro_next:
                raise osv.except_osv('Error !', 
                        'Referencia: %s \n' 
                        'El número del comprobante debería ser %s y no %s' % (
                        str(invoice.number), str(cbte_nro_next), str(cbte_nro)))

            # invoice number range (from - to) and date:
            cbt_desde = cbt_hasta = cbte_nro_next
            fecha_cbte = invoice.date_invoice.replace("-", "")

            # due and billing dates only for concept "services" 
            concepto = invoice.pyafipws_concept
            if int(concepto) != 1:
                fecha_venc_pago = invoice.date_invoice.strftime("%Y%m%d")
                fecha_serv_desde = invoice.pyafipws_billing_start_date.replace("-", "")
                fecha_serv_hasta = invoice.pyafipws_billing_end_date.replace("-", "")
            else:
                fecha_venc_pago = fecha_serv_desde = fecha_serv_hasta = None

            # customer tax number:
            nro_doc = invoice.partner_id.vat.replace("-","")
            if nro_doc.startswith("AR"):
                nro_doc = nro_doc[2:]
            if int(nro_doc)  == 0:
                tipo_doc = 99           # consumidor final
            elif len(nro_doc) < 11:
                tipo_doc = 96           # DNI
            else:
                tipo_doc = 80           # CUIT

            # invoice amount totals:
            imp_total = str("%.2f" % abs(invoice.amount_total))
            imp_tot_conc = "0.00"
            imp_neto = str("%.2f" % abs(invoice.amount_untaxed))
            imp_iva = str("%.2f" % abs(invoice.amount_tax))
            imp_trib = "0.00"
            imp_op_ex = "0.00"
            if invoice.currency_id.name == 'ARS':                
                moneda_id = "PES"
                moneda_ctz = 1
            else:
                moneda_id = {'USD':'DOL'}[invoice.currency_id.name]
                moneda_ctz = str(invoice.currency_id.rate)

            # create the invoice internally in the helper 
            wsfev1.CrearFactura(concepto, tipo_doc, nro_doc, tipo_cbte, punto_vta,
                cbt_desde, cbt_hasta, imp_total, imp_tot_conc, imp_neto,
                imp_iva, imp_trib, imp_op_ex, fecha_cbte, fecha_venc_pago, 
                fecha_serv_desde, fecha_serv_hasta,
                moneda_id, moneda_ctz)

            # analyze VAT (IVA) and other taxes (tributo):
            for tax_line in invoice.tax_line:
                if "IVA" in tax_line.name:
                    if '0%' in tax_line.name:
                        iva_id = 3
                    elif '10,5%' in tax_line.name:
                        iva_id = 4
                    elif '21%' in tax_line.name:
                        iva_id = 5
                    elif '27%' in tax_line.name:
                        iva_id = 6
                    else:
                        ivva_id = 0
                    base_imp = ("%.2f" % abs(tax_line.base))
                    importe = ("%.2f" % abs(tax_line.amount))
                    # add the vat detail in the helper
                    wsfev1.AgregarIva(iva_id, base_imp, importe)
                else:
                    if 'impuesto' in tax_line.name.lower():
                        tributo_id = 1  # nacional
                    elif 'iibbb' in tax_line.name.lower():
                        tributo_id = 3  # provincial
                    elif 'tasa' in tax_line.name.lower():
                        tributo_id = 4  # municipal
                    else:
                        tributo_id = 99
                    desc = tax_line.name
                    base_imp = ("%.2f" % abs(tax_line.base))
                    importe = ("%.2f" % abs(tax_line.amount))
                    alic = "%.2f" % tax_line.base
                    # add the other tax detail in the helper
                    wsfev1.AgregarTributo(id, desc, base_imp, alic, importe)                    

            # Request the authorization! (call AFIP webservice method)
            try:    
                wsfev1.CAESolicitar()
            except SoapFault as fault:
                print fault.faultcode
                print fault.faultstring
                msg = 'Falla SOAP %s: %s' % (fault.faultcode, fault.faultstring)
            except Exception, e:
                if wsaa.Excepcion:
                    # get the exception already parsed by the helper
                    msg = wsfev1.Excepcion
                else:
                    # avoid encoding problem when reporting exceptions to the user:
                    msg = traceback.format_exception_only(sys.exc_type, 
                                                              sys.exc_value)[0]
            else:
                msg = u"\n".join([wsfev1.Obs, wsfev1.ErrMsg])
            # calculate the barcode:
            if wsfev1.CAE:
                bars = ''.join([str(wsfev1.Cuit), "%02d" % int(tipo_cbte), 
                                  "%04d" % int(punto_vta), 
                                  str(wsfev1.CAE), wsfev1.Vencimiento])
                bars = bars + self.pyafipws_verification_digit_modulo10(bars)
            else:
                bars = ""
            # store the results
            self.write(cr, uid, invoice.id, 
                       {'pyafipws_cae': wsfev1.CAE,
                        'pyafipws_cae_due_date': wsfev1.Vencimiento,
                        'pyafipws_result': wsfev1.Resultado,
                        'pyafipws_message': msg,
                        'pyafipws_xml_request': wsfev1.XmlRequest,
                        'pyafipws_xml_response': wsfev1.XmlResponse,
                        'pyafipws_barcode': bars,
                       })
 

    def pyafipws_verification_digit_modulo10(self, codigo):
        "Calculate the verification digit 'modulo 10'"
        # http://www.consejo.org.ar/Bib_elect/diciembre04_CT/documentos/rafip1702.htm
        # Step 1: sum all digits in odd positions, left to right
        codigo = codigo.strip()
        if not codigo or not codigo.isdigit():
            return ''
        etapa1 = sum([int(c) for i,c in enumerate(codigo) if not i%2])
        # Step 2: multiply the step 1 sum by 3
        etapa2 = etapa1 * 3
        # Step 3: start from the left, sum all the digits in even positions
        etapa3 = sum([int(c) for i,c in enumerate(codigo) if i%2])
        # Step 4: sum the results of step 2 and 3
        etapa4 = etapa2 + etapa3
        # Step 5: the minimun value that summed to step 4 is a multiple of 10
        digito = 10 - (etapa4 - (int(etapa4 / 10) * 10))
        if digito == 10:
            digito = 0
        return str(digito)


electronic_invoice()


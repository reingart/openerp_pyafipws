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
# Based on code "l10n_ar_wsafip" by OpenERP - Team de Localización Argentina

"Electronic Invoice for Argentina Federal Tax Administration (AFIP) webservices"

__author__ = "Mariano Reingart (reingart@gmail.com)"
__copyright__ = "Copyright (C) 2013 Mariano Reingart and others"
__license__ = "AGPL 3.0+"

from osv import fields, osv
try:
    from openerp.tools.translate import _
except:
    _ = str
    
DEBUG = True


class journal_pyafipws_electronic_invoice(osv.osv):
    _name = "account.journal"
    _inherit = "account.journal"
    _columns = {
        'pyafipws_electronic_invoice': fields.boolean(
            _('AFIP WS electronic invoice'), 
            help="Habilita la facturación electrónica por webservices AFIP"),
    }

    def test_pyafipws_dummy(self, cr, uid, ids, context=None):
        # import AFIP webservice helper for electronic invoice
        from pyafipws.wsfev1 import WSFEv1
        wsfev1 = WSFEv1()
        # connect to the webservice and call to the test method
        wsfev1.Conectar()
        wsfev1.Dummy()
        msg = "AFIP AppServerStatus: %s DbServerStatus: %s AuthServerStatus: %s" 
        msg = msg % (
                wsfev1.AppServerStatus, 
                wsfev1.DbServerStatus,
                wsfev1.AuthServerStatus)        
        self.log(cr, uid, ids[0], msg) 
        return {}
    

journal_pyafipws_electronic_invoice()


if __name__ == "__main__":
    # basic tests:
    from osv import cursor

    

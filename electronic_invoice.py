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


journal_pyafipws_electronic_invoice()


if __name__ == "__main__":
    # basic tests:
    from osv import cursor

    

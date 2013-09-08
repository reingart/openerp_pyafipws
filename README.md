openerp_pyafipws
================

OpenERP module for Argentina's Electronic Invoicing and related webservices

Features:
 * Electronic Invoices: CAE autorization 
 * Barcode image generation
 * PDF Invoice report using templates + visual designer (TODO)
 * Wizard to verify elctronic invoices (TODO)

Extended Objects:
 * Company: certificate + private key fields and authentication function / test
 * Account Journal: invoice type fields, webservice configuration and tests
 * Account Invoice: autorization on workflow, showing CAE and barcode on the view
 * Setup system parameters: pyafipws.cache, pyafipws.proxy, pyafipws.*.url

AFIP Webservices Supported:
 * WSAA: authentication
 * WSFEv1: home market (new current version)
 * WSMTXCA: home market with product details
 * WSFEXv1: exports / foreign trade
 * WSBFE: fiscal bonus (TODO)

For more information see:
 * http://www.sistemasagiles.com.ar/trac/wiki/PyAfipWs
 * https://code.google.com/p/pyafipws/
 * http://www.afip.gov.ar/ws

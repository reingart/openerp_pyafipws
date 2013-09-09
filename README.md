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

Contact info:
 * Community forum/group: https://groups.google.com/forum/#!forum/pyafipws
 * Commercial Support: http://www.sistemasagiles.com.ar/ pyafipws@sistemasagiles.com.ar +54 (011) 4450-0716

Installation:
-------------

 * Download openerp_pyafipws from https://github.com/reingart/openerp_pyafipws/archive/master.zip
 * Unpack openerp_pyafipws inside an openerp addons folder (i.e. /usr/share/openerp/addons/)
 * Download pyafipws from https://github.com/reingart/pyafipws/archive/master.zip
 * Unpack pyafipws inside the module folder (openerp_pyafipws), rename it to just pyafipws

To install the dependencies, follow: https://code.google.com/p/pyafipws/wiki/InstalacionCodigoFuente

OpenERP Configuration:
----------------------
 
In Settings, Companies, open it and go to the tab "Argentina AfipWS":
 * Complete the authorized CUIT (VAT, only numbers)
 * Complete the Certificate and Private Key (open .CRT and .KEY, copy and paste text)
 * Press the "Test" button to see if everithing is ok.

In Accounting, Configuration, Financial Accounting, Journals, 
create a new jornal for electronic invoices it and tab "Argentina Afip WebServices":
 * Select the webservice (home market, exports, etc)
 * Select the invoice type (A: general regime, B: final consumer C: exempt / monotributo, E: exports)
 * Complete the point of sale prefix (anyone for testing, register one at AFIP for production). 
 * Test them ussing the buttons "Dummy", "Verificar" (verify) y "Obtener últ.nro." (get last invoice number)
 * Remember that the sequence numeration must match AFIP (starts at 1).

If everything went ok, you should see the tab "Factura Electronica Argentina" in Accounting, Customers, Invoices.
By default, invoice type will be 1 (products), you can select 2 (services) and complete the billing period dates.
When you click Validate to pass from draft to open, it will call AFIP and complete the result field, 
CAE (electronico invoice autorization number), CAE due date and messages.

For testing you don't need to change the system setting. 
For production you must set:

 * pyafipws.wsaa.url = https://wsaa.afip.gov.ar/ws/services/LoginCms?wsdl
 * pyafipws.wsfe.url = https://servicios1.afip.gov.ar/wsfev1/service.asmx?WSDL
 * pyafipws.wsfex.url = https://servicios1.afip.gov.ar/wsfexv1/service.asmx?WSDL

Optionally, create a temporary cache folder (i.a. /tmp/cache), give openerp write permissions
and configure system parameter pyafipws.cache = /tmp/cache
If you use special proxy servers (ISA), you would need to install pycurl 
and configure pyafipws.proxy system parameter accordingly.

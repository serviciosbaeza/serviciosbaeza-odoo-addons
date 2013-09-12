# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2012 Pedro Manuel Baeza Romero All Rights Reserved.
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Periodical invoicing',
    'version': '1.2',
    'category': 'Accounting',
    'description': """Module for making easily periodical invoices to customers from agreements that allow to set:
    * Agreement term
    * Products and quantities to invoice
    * Special prices and discounts
    """,
    'author': 'Serv. Tecnolog. Avanzados - Pedro M. Baeza',
    'website' : 'http://www.serviciosbaeza.com',
    'depends': ['account', 'sale'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/renew_wizard_view.xml', 
        'periodical_invoicing_data.xml', 
        'periodical_invoicing_view.xml',
        'sale_order_view.xml',
    ],
    'auto_install': False,
    "installable": True,
}


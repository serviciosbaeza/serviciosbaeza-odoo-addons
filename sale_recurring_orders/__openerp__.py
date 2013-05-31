# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2012 Serv. Tecnol. Avanzados (http://www.serviciosbaeza.com) All Rights Reserved.
#                       Pedro M. Baeza <pedro.baeza@serviciosbaeza.com> 
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
    'name': 'Recurring orders',
    'version': '1.2',
    'category': 'Sales & Purchase',
    'description': """
    Module for making easyly recurring orders to partners from agreements that allow to set:
    * Agreement term
    * Products, quantities and discounts to include
    * Custom description in agreement lines
    * Ordering intervals for each product
    """,
    'author': 'Serv. Tecnolog. Avanzados - Pedro M. Baeza',
    'website' : 'http://www.serviciosbaeza.com',
    'depends': ['sale'],
    'data': [
        'security/ir.model.access.csv',
        'recurring_orders_data.xml', 
        'wizard/renew_wizard_view.xml', 
        'recurring_orders_view.xml',
        'sale_order_view.xml',
    ],
    'auto_install': False,
    "installable": True,
}


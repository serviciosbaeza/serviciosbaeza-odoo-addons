# -*- coding: utf-8 -*-
# (c) 2015 Serv. Tecnol. Avanzados - Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Recurring orders',
    'version': '1.2',
    'category': 'Sales & Purchase',
    'author': 'Serv. Tecnol. Avanzados - Pedro M. Baeza',
    'website': 'http://www.serviciosbaeza.com',
    'depends': ['sale'],
    'data': [
        'security/ir.model.access.csv',
        'data/recurring_orders_data.xml',
        'wizard/renew_wizard_view.xml',
        'views/recurring_orders_view.xml',
        'views/sale_order_view.xml',
    ],
    "installable": True,
}

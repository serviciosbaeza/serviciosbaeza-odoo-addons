# -*- coding: utf-8 -*-
# (c) 2015 Serv. Tecnol. Avanzados - Pedro M. Baeza
# Copyright 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Recurring orders',
    'version': '8.0.2.2.0',
    'category': 'Sales & Purchase',
    'author': 'Serv. Tecnol. Avanzados - Pedro M. Baeza',
    'website': 'http://www.serviciosbaeza.com,'
               'Tecnativa',
    'depends': ['sale'],
    'data': [
        'security/ir.model.access.csv',
        'data/recurring_orders_data.xml',
        'wizard/renew_wizard_view.xml',
        'views/recurring_orders_view.xml',
        'views/sale_order_view.xml',
        'views/res_partner_view.xml',
    ],
    "installable": True,
}

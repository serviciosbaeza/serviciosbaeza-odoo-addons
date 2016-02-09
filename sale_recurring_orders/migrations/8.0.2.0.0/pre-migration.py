# -*- coding: utf-8 -*-
# (c) 2016 Serv. Tecnol. Avanzados - Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(cr, version):
    openupgrade.rename_columns(
        cr, {'sale_order': [('from_agreement', None)]})
    # Precreate agreement_id column for filling it with the information
    # supplied by sale.recurring_orders.agreement.order model (that is removed
    # in this version)
    cr.execute('ALTER TABLE sale_order ADD COLUMN agreement_id int')
    openupgrade.logged_query(
        cr,
        """
        UPDATE sale_order
        SET agreement_id=agreement_order.agreement_id
        FROM sale_recurring_orders_agreement_order AS agreement_order
        WHERE agreement_order.order_id = sale_order.id
        """)

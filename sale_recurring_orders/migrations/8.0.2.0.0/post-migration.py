# -*- coding: utf-8 -*-
# (c) 2016 Serv. Tecnol. Avanzados - Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(cr, version):
    """Fill not linked sales orders."""
    openupgrade.logged_query(
        cr,
        """
        UPDATE sale_order
        SET agreement_id=agreement.id
        FROM sale_recurring_orders_agreement AS agreement
        WHERE sale_order.origin = agreement.number
            AND sale_order.%s = True
            AND sale_order.agreement_id is NULL
        """ % openupgrade.get_legacy_name('from_agreement'))

# -*- coding: utf-8 -*-
# Copyright 2017 Tecnativa - Vicent Cubells <vicent.cubells@tecnativa.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


_column_renames = {
    'account_periodical_invoicing_agreement': [
        ('prolong_unit', None, None),
    ],
}

_field_renames = [
    ('account.analytic.account', 'account_analytic_account',
     'start_date', 'date_start'),
    ('account.analytic.account', 'account_analytic_account',
     'prolong_interval', 'recurring_interval'),
    ('account.analytic.account', 'account_analytic_account',
     'agreement_line', 'recurring_invoice_line_ids'),
    ('account.analytic.account', 'account_analytic_account',
     'number', 'code'),
    ('account.analytic.account', 'account_analytic_account',
     'period_type', 'recurring_invoicing_type'),
    ('account.analytic.invoice.line', 'account_analytic_invoice_line',
     'agreement_id', 'analytic_account_id'),
    ('account.analytic.invoice.line', 'account_analytic_invoice_line',
     'price', 'price_unit'),
]

_table_renames = [
    ('account_periodical_invoicing_agreement_line',
     'account_analytic_invoice_line'),
]

_model_renames = [
    ('account_periodical_invoicing_agreement_line',
     'account_analytic_invoice_line'),
]


def _migrate_account_periodical_invoicing(env):
    """If account_periodical_invoicing is installed. In v9 now it's
    integrated on 'contract' module."""
    openupgrade.update_module_names(
        env.cr,
        [('account_periodical_invoicing', 'contract')],
        merge_modules=True,
    )


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    openupgrade.copy_columns(env.cr, _column_renames)
    openupgrade.rename_models(env.cr, _model_renames)
    openupgrade.rename_tables(env.cr, _table_renames)
    openupgrade.field_renames(env, _field_renames)
    openupgrade.map_values(
        env.cr,
        openupgrade.get_legacy_name('prolong_unit'),
        'recurring_rule_type',
        [
            ('days', 'daily'),
            ('weeks', 'weekly'),
            ('months', 'monthly'),
            ('years', 'yearly'),
        ], table='account_analytic_account',
    )
    # Merge account_periodical_invoicing into contract
    _migrate_account_periodical_invoicing(env)
    # Set name in lines as It is required
    openupgrade.logged_query(env.cr, """
        UPDATE account_analytic_invoice_line aail
        SET uom_id = pt.uom_id,
            name = CONCAT(
                '[', pd.default_code, '] ', pt.name,
                aail.additional_description
                )
        FROM product_product pd, product_template pt
        WHERE aail.product_id = pd.id
        AND pd.product_tmpl_id = pt.id
    """)
    # Set contract_id on invoices
    openupgrade.logged_query(env.cr, """
        UPDATE account_invoice ai
        SET contract_id  = ag.agreement_id
        FROM account_periodical_invoicing_agreement_invoice ag
        WHERE ag.invoice_id = ai.id;
    """)
    # Set contract module to upgrade
    env.cr.execute("""
        UPDATE ir_module_module
        SET state = 'to upgrade'
        WHERE module = 'contract'
      """)

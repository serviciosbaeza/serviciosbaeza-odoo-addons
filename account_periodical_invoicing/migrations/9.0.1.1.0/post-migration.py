# -*- coding: utf-8 -*-
# Copyright 2017 Tecnativa - Vicent Cubells <vicent.cubells@tecnativa.com>
# Copyright 2017 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade
from openerp import fields


_column_copies = {
    'account_periodical_invoicing_agreement_line': [
        ('invoicing_unit', None, None),
    ],
}

# Made after table renaming
_field_renames = [
    ('account.analytic.invoice.line', 'account_analytic_invoice_line',
     'price', 'price_unit'),
]

_table_renames = [
    ('account_periodical_invoicing_agreement_line',
     'account_analytic_invoice_line'),
]

_model_renames = [
    ('account.periodical_invoicing.agreement.line',
     'account.analytic.invoice.line'),
]


def _store_next_invoice_date(env):
    """On this module, the next invoice date is computed each time, but
    contract module has a field for that. We precompute it on a column now
    for having it on SQL operations.

    Made before table rename.
    """
    env.cr.execute("ALTER TABLE account_periodical_invoicing_agreement_line "
                   "ADD recurring_next_date DATE")
    Agreement = env['account.periodical_invoicing.agreement']
    lines = env[
        'account.periodical_invoicing.agreement.line'
    ].search([])
    for line in lines:
        last_invoice_date = fields.Date.from_string(
            line.last_invoice_date or fields.Date.today()
        )
        next_invoice_date = Agreement._get_next_invoice_date(
            line.agreement_id, line, last_invoice_date,
        )
        env.cr.execute(
            """UPDATE account_periodical_invoicing_agreement_line
            SET recurring_next_date = %s""",
            (fields.Date.to_string(next_invoice_date), )
        )


def _create_analytic_account_records(env):
    """As account_analytic_account table already exists (and may contain
    other records), we can't just drop and rename the agreement table.
    Insted, we need to:

    * Adapt table structure.
    * Insert records in the table.
    * Change parent reference in the lines to new created records.

    There's a special case for agreements with lines with several invoicing
    units. We have to split them in several contracts.
    """
    if not openupgrade.column_exists(
            env.cr, 'account_analytic_account', 'recurring_invoices'
    ):
        # account_analytic_analysis is not installed
        env.cr.execute("ALTER TABLE account_analytic_account "
                       "ADD recurring_invoices BOOLEAN")
        env.cr.execute("ALTER TABLE account_analytic_account "
                       "ADD recurring_interval INTEGER")
        env.cr.execute("ALTER TABLE account_analytic_account "
                       "ADD recurring_rule_type VARCHAR")
    env.cr.execute("ALTER TABLE account_analytic_account ADD date_start DATE")
    # This field is in prevision of v10, that has it
    env.cr.execute("ALTER TABLE account_analytic_account ADD date_end DATE")
    env.cr.execute("ALTER TABLE account_analytic_account "
                   "ADD recurring_invoicing_type VARCHAR")
    env.cr.execute("ALTER TABLE account_analytic_account "
                   "ADD agreement_id INTEGER")
    env.cr.execute("ALTER TABLE account_analytic_invoice_line "
                   "ADD analytic_account_id INTEGER")
    query_insert = """
        INSERT INTO account_analytic_account
        (agreement_id, date_start, date_end, code, recurring_invoicing_type,
         name, recurring_invoices, company_id, partner_id, account_type)
        SELECT id, start_date, end_date, number, period_type, name, True,
            company_id, partner_id,
            CASE
                WHEN active THEN 'normal'
                ELSE 'closed'
            END
        FROM account_periodical_invoicing_agreement
        WHERE id IN %s"""
    query_split = """
        SELECT aail.id
        FROM account_analytic_invoice_line aail,
            account_analytic_account aaa
        WHERE (aaa.recurring_rule_type != aail.invoicing_unit
            OR aaa.recurring_interval != aail.invoicing_interval)
            AND aail.analytic_account_id = aaa.id
            AND aaa.id > %s"""
    query_update = """
        UPDATE account_analytic_account aaa
        SET recurring_interval=sub.invoicing_interval,
            recurring_rule_type=sub.invoicing_unit,
            recurring_next_date=sub.recurring_next_date
        FROM (
            SELECT invoicing_interval, invoicing_unit, agreement_id,
                recurring_next_date
            FROM account_analytic_invoice_line
            WHERE id IN (
               SELECT min(id)
               FROM account_analytic_invoice_line
               WHERE id IN %s
               GROUP BY agreement_id
            )
        ) AS sub
        WHERE sub.agreement_id = aaa.agreement_id
            AND aaa.id > %s"""
    env.cr.execute("SELECT id FROM account_analytic_invoice_line")
    to_split_ids = [x[0] for x in env.cr.fetchall()]
    while to_split_ids:
        # Get the current max value of account_analytic_account for basing
        # the updates on that value
        env.cr.execute("SELECT max(id) FROM account_analytic_account")
        row = env.cr.fetchone()
        max_aaa_id = row[0] if row else 0
        # Insert the contract
        env.cr.execute(
            """SELECT DISTINCT(agreement_id)
            FROM account_analytic_invoice_line
            WHERE id IN %s""", (tuple(to_split_ids), )
        )
        agreement_ids = [x[0] for x in env.cr.fetchall()]
        openupgrade.logged_query(
            env.cr, query_insert, (tuple(agreement_ids), ),
        )
        # Assign analytic account to agreement lines
        openupgrade.logged_query(
            env.cr,
            """UPDATE account_analytic_invoice_line aail
            SET analytic_account_id = aaa.id
            FROM account_analytic_account aaa
            WHERE aaa.agreement_id = aail.agreement_id
                AND aail.id IN %s""", (tuple(to_split_ids), ),
        )
        # Set first line invoicing interval on the contract headers
        openupgrade.logged_query(
            env.cr, query_update, (tuple(to_split_ids), max_aaa_id, ),
        )
        # Query again if there's something remaining
        env.cr.execute(query_split, (max_aaa_id,))
        to_split_ids = [x[0] for x in env.cr.fetchall()]


def _fill_line_data(env):
    """Set name and UoM in lines from product info as they are required in
    contract. Column uom_id doesn't exist still.

    It also maps values for invoicing interval for preparing them.

    Made after table renaming.
    """
    env.cr.execute("ALTER TABLE account_analytic_invoice_line "
                   "ADD uom_id INTEGER")
    env.cr.execute("ALTER TABLE account_analytic_invoice_line "
                   "ADD name VARCHAR")
    openupgrade.logged_query(env.cr, """
        UPDATE account_analytic_invoice_line aail
        SET uom_id = pt.uom_id,
            name = CASE
                WHEN pd.default_code IS NOT NULL THEN
                    '[' || pd.default_code || '] ' || pt.name || ' ' ||
                    aail.additional_description
                ELSE pt.name || ' ' || aail.additional_description
            END
        FROM product_product pd, product_template pt
        WHERE aail.product_id = pd.id
        AND pd.product_tmpl_id = pt.id
    """)
    # Map values for not making the conversion on the insert SQL
    openupgrade.map_values(
        env.cr,
        openupgrade.get_legacy_name('invoicing_unit'),
        'invoicing_unit',
        [
            ('days', 'daily'),
            ('weeks', 'weekly'),
            ('months', 'monthly'),
            ('years', 'yearly'),
        ], table='account_analytic_invoice_line',
    )


def _invoice_set_contract_reference(env):
    """Set the reference to the contract (new ID) in the invoices."""
    env.cr.execute("ALTER TABLE account_invoice ADD contract_id INTEGER")
    openupgrade.logged_query(env.cr, """
        UPDATE account_invoice ai
        SET contract_id  = aaa.id
        FROM account_periodical_invoicing_agreement_invoice ag,
            account_analytic_account aaa
        WHERE ag.invoice_id = ai.id
            AND aaa.agreement_id = ag.agreement_id
    """)


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    _store_next_invoice_date(env)
    openupgrade.copy_columns(env.cr, _column_copies)
    # This exists in account_analytic_analysis
    if openupgrade.table_exists(env.cr, 'account_analytic_invoice_line'):
        env.cr.execute("DROP TABLE account_analytic_invoice_line")
        openupgrade.update_module_names(
            env.cr, [('account_analytic_analysis',
                      'account_periodical_invoicing')],
            merge_modules=True,
        )
    else:
        openupgrade.rename_models(env.cr, _model_renames)
    openupgrade.rename_tables(env.cr, _table_renames)
    openupgrade.rename_fields(env, _field_renames)
    _fill_line_data(env)
    _create_analytic_account_records(env)
    _invoice_set_contract_reference(env)
    # mark contract module to be upgraded
    env.cr.execute("UPDATE ir_module_module SET state = 'to upgrade' "
                   "WHERE name = 'contract'")

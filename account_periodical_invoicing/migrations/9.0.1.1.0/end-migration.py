# -*- coding: utf-8 -*-
# Copyright 2017 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def _set_modules_state(env):
    """Transform account_periodical_invoicing into contract with a merge
    operation as the other module should exist."""
    openupgrade.update_module_names(
        env.cr,
        [('account_periodical_invoicing', 'contract')],
        merge_modules=True,
    )


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    _set_modules_state(env)

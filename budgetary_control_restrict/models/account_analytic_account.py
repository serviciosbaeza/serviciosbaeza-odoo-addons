# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2014 Serv. Tecnol. Avanzados (http://www.serviciosbaeza.com)
#                       Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
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
from openerp import models, api, exceptions, _


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    @api.one
    @api.constrains('account_id', 'date', 'amount')
    def _check_budget(self):
        budget_obj = self.env['budgetary.control']
        budgets = budget_obj.search([('date_start', '<=', self.date),
                                     ('date_end', '>=', self.date),
                                     '|',
                                     ('company_id', '=', self.company_id.id),
                                     ('company_id', '=', False)])
        budget_line_obj = self.env['budgetary.control.line']
        budget_lines = budget_line_obj.search(
            [('budgetary', 'in', budgets.ids),
             ('analytic_account', '=', self.account_id.id)])
        if budget_lines:
            if (budget_lines.amount_allocated < budget_lines.amount < 0 and
                    budget_lines.budgetary.user_id.id != self.env.uid):
                raise exceptions.Warning(
                    _('The amount requested exceeds the allowed budget for '
                      'this analytic account: %s. Please contact your budget '
                      'responsible for unlocking the order.') %
                    budget_lines.analytic_account.complete_name)

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
from openerp import models, fields, api
import openerp.addons.decimal_precision as dp


class BudgetaryControl(models.Model):
    _name = 'budgetary.control'

    @api.one
    @api.depends('lines.amount')
    def _get_total(self):
        total = 0.0
        for line in self.lines:
            total += line.amount
        self.total_amount = total

    @api.one
    @api.depends('lines.amount_allocated')
    def _get_total_allocated(self):
        total = 0.0
        for line in self.lines:
            total += line.amount_allocated
        self.total_amount_allocated = total

    name = fields.Char(string="Name")
    date_start = fields.Date(string='Start date', required=True)
    date_end = fields.Date(string='End date', required=True)
    lines = fields.One2many(comodel_name='budgetary.control.line',
                            inverse_name='budgetary',
                            string="Budgetary control lines")
    user_id = fields.Many2one(comodel_name='res.users', string="Responsible",
                              required=True, default=lambda self: self.env.uid)
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: (
            self.env['res.company']._company_default_get('budgetary.control')))
    total_amount = fields.Float(string="Total amount", compute=_get_total)
    total_amount_allocated = fields.Float(string="Total amount allocated",
                                          compute=_get_total_allocated)


class BudgetaryControlLine(models.Model):
    _name = 'budgetary.control.line'

    @api.one
    @api.depends('analytic_account', 'analytic_account.analytic_lines')
    def _get_allocated(self):
        analytic_line_obj = self.env['account.analytic.line']
        domain = [('account_id', '=', self.analytic_account.id),
                  ('date', '>=', self.budgetary.date_start),
                  ('date', '<=', self.budgetary.date_end)]
        if self.budgetary.company_id:
            domain.append(('company_id', '=', self.budgetary.company_id.id))
        analytic_lines = analytic_line_obj.search(domain)
        amount = 0.0
        for analytic_line in analytic_lines:
            amount += analytic_line.amount
        self.amount_allocated = amount

    budgetary = fields.Many2one(
        comodel_name='budgetary.control', required=True,
        string="Parent budgetary control")
    analytic_account = fields.Many2one(
        comodel_name='account.analytic.account', string='Analytic account',
        required=True, domain=[('type', '!=', 'view')])
    amount = fields.Float(string="Amount allowed", required=True,
                          digits_compute=dp.get_precision('Account'))
    amount_allocated = fields.Float(
        string="Amount allocated", required=True, compute=_get_allocated,
        digits_compute=dp.get_precision('Account'), readonly=True)

    _sql_constraints = [
        ('budgetary_account_uniq', 'unique (budgetary, analytic_account)',
         'There must be only one line per analytic account'),
    ]

# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2014 Serv. Tecnol. Avanzados (http://www.serviciosbaeza.com)
#                       Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>
#    Copyright (c) 2015 Antiun Ingenieria, SL (http://www.antiun.com)
#                       Antonio Espinosa <antonioea@antiun.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp import models, fields, api
from datetime import datetime


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    date_time = fields.Datetime(default=fields.Datetime.now, string='Date')
    include_in_task_work_view = fields.Boolean(
        related='task_id.stage_id.include_in_task_work_view', readonly=True,
        store=True)

    @api.onchange('account_id')
    def onchange_account_id(self):
        if not self.account_id:
            return {'domain': {'task_id': []}}
        self.task_id = False
        project = self.env['project.project'].search(
            [('analytic_account_id', '=', self.account_id.id)], limit=1)
        return {
            'domain': {
                'task_id': [('project_id', '=', project.id),
                            ('include_in_task_work_view', '=', True)]},
        }

    @api.onchange('task_id')
    def onchange_task_id(self):
        if self.task_id:
            self.account_id = self.task_id.project_id.analytic_account_id.id

    def create(self, vals):
        if 'date_time' in vals and 'date' not in vals:
            vals['date'] = fields.Date.from_string(vals['date_time'])
        return super(AccountAnalyticLine, self).create(vals)

    def write(self, vals):
        if 'date_time' in vals and 'date' not in vals:
            vals['date'] = fields.Date.from_string(vals['date_time'])
        return super(AccountAnalyticLine, self).write(vals)

    @api.multi
    def button_end_work(self):
        end_date = datetime.now()
        for work in self:
            date = fields.Datetime.from_string(work.date_time)
            work.unit_amount = (end_date - date).total_seconds() / 3600
        return True

    @api.multi
    def button_open_task(self):
        stage = self.env['project.task.type'].search(
            [('include_in_task_work_view', '=', True)], limit=1)
        self.mapped('task_id').write({'stage_id': stage.id})

    @api.multi
    def button_close_task(self):
        stage = self.env['project.task.type'].search(
            [('include_in_task_work_view', '=', False)], limit=1)
        self.mapped('task_id').write({'stage_id': stage.id})

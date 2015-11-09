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


class ProjectWork(models.Model):
    _inherit = 'project.task.work'

    project = fields.Many2one(
        string='Project', related='task_id.project_id', store=True,
        domain="[('state', 'not in', ('template', 'cancelled', 'close'))]")
    include_in_task_work_view = fields.Boolean(
        related='task_id.stage_id.include_in_task_work_view', readonly=True,
        store=True)

    @api.onchange('project')
    def onchange_project(self):
        if not self.project:
            return {'domain': {'task_id': []}}
        return {
            'domain': {
                'task_id': [('project_id', '=', self.project.id),
                            ('include_in_task_work_view', '=', True)]},
        }

    @api.onchange('task_id')
    def onchange_task_id(self):
        if not self.task_id:
            return {}
        return {'value': {'project': self.task_id.project_id.id}}

    @api.multi
    def button_end_work(self):
        end_date = datetime.now()
        for work in self:
            date = fields.Datetime.from_string(work.date)
            work.hours = (end_date - date).total_seconds() / 3600
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

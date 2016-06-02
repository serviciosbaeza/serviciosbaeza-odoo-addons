# -*- coding: utf-8 -*-
# © 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    ordered_works = fields.Many2many(
        comodel_name="project.task.work", compute="_compute_ordered_works")
    total_work_hours = fields.Float(
        compute="_compute_total_work_hours")

    @api.multi
    def _compute_ordered_works(self):
        for task in self:
            works = task.work_ids
            self.ordered_works = works.sorted(
                key=lambda x: x.date, reverse=True)

    @api.multi
    @api.depends('work_ids')
    def _compute_total_work_hours(self):
        for task in self:
            task.total_work_hours = sum(task.mapped('work_ids.hours'))

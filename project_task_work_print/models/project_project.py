# -*- coding: utf-8 -*-
##############################################################################
# (c) 2015 Pedro M. Baeza
# License AGPL-3 - See LICENSE file on root folder for details
##############################################################################
from openerp import models, fields, api


class ProjectProject(models.Model):
    _inherit = "project.project"

    ordered_works = fields.Many2many(
        comodel_name="project.task.work", compute="_compute_ordered_works")

    @api.one
    def _compute_ordered_works(self):
        works = self.mapped('task_ids.work_ids')
        self.ordered_works = works.sorted(key=lambda x: x.date, reverse=True)

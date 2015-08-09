# -*- coding: utf-8 -*-
# (c) 2015 Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, fields


class ProjectTask(models.Model):
    _inherit = 'project.task'

    include_in_task_work_view = fields.Boolean(
        related='stage_id.include_in_task_work_view')

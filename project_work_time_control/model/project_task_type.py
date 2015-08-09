# -*- coding: utf-8 -*-
# (c) 2015 Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, fields


class ProjectTaskType(models.Model):
    _inherit = 'project.task.type'

    include_in_task_work_view = fields.Boolean(
        string="Include in the task work fast-encoding view", default=True,
        help="If you mark this check, tasks that are in this stage will be "
             "selectable in the 'Tasks works' fast-encoding view.")

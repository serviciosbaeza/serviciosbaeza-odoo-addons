# -*- coding: utf-8 -*-
# © 2014-2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import time
from openerp.report import report_sxw


class TaskTaskWorkReport(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context=None):
        super(TaskTaskWorkReport, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
        })
        self.context = context

report_sxw.report_sxw(
    'report.project.task.work.task', 'project.task',
    'addons/project_task_work_print/report/task_taskwork_report.rml',
    parser=TaskTaskWorkReport)

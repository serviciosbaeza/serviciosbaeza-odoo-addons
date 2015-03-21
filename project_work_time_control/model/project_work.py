# -*- coding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
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
from openerp.osv import orm, fields
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.addons.project.project import _TASK_STATE
from datetime import datetime


class project_work(orm.Model):
    _inherit = "project.task.work"

    _columns = {
        'project': fields.related(
            'task_id', 'project_id', type="many2one", string="Project",
            relation="project.project", store=True),
        'task_state': fields.related(
            'task_id', 'state', type="selection", string="Task state",
            selection=_TASK_STATE, readonly=True),
    }

    def onchange_project(self, cr, uid, ids, project_id, context=None):
        domain = [('state', 'in', ('draft', 'open', 'pending'))]
        if project_id:
            domain.append(('project_id', '=', project_id))
        return {
            'domain': {'task_id': domain},
        }

    def onchange_task_id(self, cr, uid, ids, task_id, context=None):
        if not task_id:
            return {}
        task = self.pool['project.task'].browse(cr, uid, task_id,
                                                context=context)
        return {'value': {'project': task.project_id.id}}

    def button_end_work(self, cr, uid, ids, context=None):
        end_date = datetime.now()
        for work in self.browse(cr, uid, ids, context=context):
            date = datetime.strptime(work.date, DEFAULT_SERVER_DATETIME_FORMAT)
            hours = (end_date - date).total_seconds() / 3600
            self.write(cr, uid, [work.id], {'hours': hours}, context=context)
        return True

    def button_open_task(self, cr, uid, ids, context=None):
        for task_work in self.browse(cr, uid, ids, context=context):
            task_work.task_id.project_task_reevaluate(context=context)

    def button_close_task(self, cr, uid, ids, context=None):
        for task_work in self.browse(cr, uid, ids, context=context):
            task_work.task_id.action_close(context=context)

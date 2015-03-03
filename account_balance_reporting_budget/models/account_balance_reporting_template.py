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
from openerp.osv import orm, fields
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp


class TemplateLine(orm.Model):
    _inherit = "account.balance.reporting.template.line"

    _columns = {
        'budget_lines': fields.one2many(
            'account.balance.reporting.template.line.budget', 'line_id',
            'Budget lines'),
    }

    def view_budget_lines(self, cr, uid, ids, context=None):
        """Method for viewing associated budget lines."""
        ctx = context.copy()
        ctx['default_line_id'] = ids[0]
        ctx['allow_create'] = True
        # Return view with budget lines
        return {
            'name': _('Budget lines'),
            'domain': "[('line_id', 'in', %s)]" % ids,
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'account.balance.reporting.template.line.budget',
            'context': ctx,
            'type': 'ir.actions.act_window',
        }


class TemplateLineBudget(orm.Model):
    _name = "account.balance.reporting.template.line.budget"

    _columns = {
        'line_id': fields.many2one('account.balance.reporting.template.line',
                                   'Report line reference', required=True),
        'period_id': fields.many2one('account.period',
                                     'Period', required=True),
        'estimated_value': fields.float(
            string='Estimated value',
            digits_compute=dp.get_precision('Account')),
    }

    _sql_constraints = [('unique budget line',
                         'UNIQUE(line_id, period_id)',
                         'Each period can have only one budget line')]

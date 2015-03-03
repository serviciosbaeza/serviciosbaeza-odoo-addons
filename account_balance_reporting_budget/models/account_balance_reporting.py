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
import openerp.addons.decimal_precision as dp


class TemplateLine(orm.Model):
    _inherit = "account.balance.reporting.line"

    def _get_estimated_value(self, cr, uid, ids, name, args, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            period_ids = line.report_id.current_period_ids or []
            if not period_ids:
                period_ids = line.report_id.current_fiscalyear_id.period_ids
            res[line.id] = 0.0
            for budget_line in line.template_line_id.budget_lines:
                if budget_line.period_id in period_ids:
                    res[line.id] += budget_line.estimated_value
        return res

    def _get_difference(self, cr, uid, ids, name, args, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            diff = line.current_value - line.estimated_value
            res[line.id] = {
                'difference': diff,
                'deviation': (line.estimated_value and
                              diff / line.estimated_value or 0.0) * 100,
            }
        return res

    _columns = {
        'estimated_value': fields.function(
            _get_estimated_value, store=True, string='Estimated value',
            type="float", digits_compute=dp.get_precision('Account')),
        'difference': fields.function(
            _get_difference, string='Difference', multi=True, store=True,
            type="float", digits_compute=dp.get_precision('Account'),
            help="Variation between real value and estimated"),
        'deviation': fields.function(
            _get_difference, multi=True, string='Deviation (%)', store=True,
            type="float", help="Percentage of deviation between calculated "
                               "difference and the real value."),
    }

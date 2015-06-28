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
from openerp import models, fields, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.multi
    def action_cancel(self):
        res = super(PurchaseOrder, self).action_cancel()
        for order in self:
            for po_line in order.order_line:
                if po_line.analytic_line:
                    po_line.analytic_line.unlink()
        return res


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    analytic_line = fields.Many2one(comodel_name='account.analytic.line',
                                    string="Analytic line")

    @api.multi
    def action_confirm(self):
        res = super(PurchaseOrderLine, self).action_confirm()
        analytic_line_obj = self.env['account.analytic.line']
        for po_line in self:
            if po_line.account_analytic_id:
                order = po_line.order_id
                journals = self.env['account.journal'].search(
                    [('type', '=', 'purchase'),
                     ('company_id', '=', order.company_id.id)],
                    limit=1)
                acc_id = order._choose_account_from_po_line(po_line)
                analytic_line_id = analytic_line_obj.create(
                    {'name': po_line.name,
                     'date': po_line.date_planned,
                     'account_id': po_line.account_analytic_id.id,
                     'unit_amount': po_line.product_qty,
                     'amount': -po_line.price_subtotal,
                     'product_id': po_line.product_id.id,
                     'product_uom_id': po_line.product_uom.id,
                     'general_account_id': acc_id,
                     'journal_id': journals[0].analytic_journal_id.id,
                     'ref': order.name})
                po_line.analytic_line = analytic_line_id
        return res

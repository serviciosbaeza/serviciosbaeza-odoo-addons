# -*- coding: utf-8 -*-
# (c) 2015 Serv. Tecnol. Avanzados - Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def action_button_generate_agreement(self):
        agreement_ids = []
        agreement_obj = self.env['sale.recurring_orders.agreement']
        agreement_line_obj = self.env['sale.recurring_orders.agreement.line']
        for sale_order in self:
            agreement = {
                'name': sale_order.name,
                'partner_id': sale_order.partner_id.id,
                'company_id': sale_order.company_id.id,
                'start_date': fields.Datetime.now(),
            }
            agreement_id = agreement_obj.create(agreement)
            agreement_ids.append(agreement_id)
            for order_line in sale_order.order_line:
                agreement_line = {
                    'agreement_id': agreement_id,
                    'product_id': order_line.product_id.id,
                    'discount': order_line.discount,
                    'quantity': order_line.product_uom_qty,
                }
                agreement_line_obj.create(agreement_line)
        if len(agreement_ids) == 1:
            # display the agreement record
            view = self.env.ref(
                'sale_recurring_orders.'
                'view_sale_recurring_orders_agreement_form')
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'sale.recurring_orders.agreement',
                'res_id': agreement_ids[0],
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': view.id,
                'target': 'current',
                'nodestroy': True,
            }
        return True

    from_agreement = fields.Boolean(
        string='From agrement?',
        help='This field indicates if the sale order comes from an agreement.')

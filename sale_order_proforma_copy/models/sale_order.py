# -*- encoding: utf-8 -*-
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
from openerp import netsvc


class SaleOrder(orm.Model):
    _inherit = "sale.order"

    _columns = {
        'state': fields.selection(
            [('draft', 'Draft Quotation'),
             ('sent', 'Quotation Sent'),
             ('proforma', 'Pro-forma'),
             ('cancel', 'Cancelled'),
             ('waiting_date', 'Waiting Schedule'),
             ('progress', 'Sales Order'),
             ('manual', 'Sale to Invoice'),
             ('shipping_except', 'Shipping Exception'),
             ('invoice_except', 'Invoice Exception'),
             ('done', 'Done')], 'Status', readonly=True,
            track_visibility='onchange', select=True,
            help="Gives the status of the quotation or sales order.\nThe "
                 "exception status is automatically set when a cancel "
                 "operation occurs in the invoice validation (Invoice "
                 "Exception) or in the picking list process (Shipping "
                 "Exception).\nThe 'Waiting Schedule' status is set when the "
                 "invoice is confirmed but waiting for the scheduler to run "
                 "on the order date."),
        'source_order': fields.many2one(
            'sale.order', string="Order reference", old_name="quotation",
            help="This field indicates the source for the proforma"),
        'proformas': fields.one2many(
            'sale.order', 'source_order', "Proformas"),
    }

    def action_proforma(self, cr, uid, ids, context=None):
        wf_service = netsvc.LocalService("workflow")
        order = self.browse(cr, uid, ids[0], context=context)
        proforma_vals = self.copy_data(
            cr, uid, ids[0], context=context,
            default={'origin': order.name,
                     'source_order': order.id,
                     'name': self.pool['ir.sequence'].next_by_code(
                         cr, uid, 'sale.order.proforma')})
        # Remove reference of previous proformas and other one2many/many2many
        del proforma_vals['proformas']
        del proforma_vals['picking_ids']
        del proforma_vals['invoice_ids']
        if 'sale_orders' in proforma_vals:
            del proforma_vals['sale_orders']
        proforma_id = self.create(cr, uid, proforma_vals, context=context)
        wf_service.trg_validate(uid, 'sale.order', proforma_id,
                                'quotation_proforma', cr)
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'res_id': proforma_id,
            'view_type': 'form',
            'view_mode': 'form',
        }

    def button_show_proformas(self, cr, uid, ids, context=None):
        order = self.browse(cr, uid, ids[0], context=context)
        if order.proformas:
            act_window = {
                'type': 'ir.actions.act_window',
                'res_model': 'sale.order',
                'view_type': 'form',
                'domain': [('id', 'in', [x.id for x in order.proformas])]
            }
            if len(order.proformas) == 1:
                act_window['view_mode'] = 'form'
                act_window['res_id'] = order.proformas[0].id
            else:
                act_window['view_mode'] = 'tree,form'
            return act_window

    def copy(self, cr, uid, rec_id, default=None, context=None):
        if not default:
            default = {}
        default['source_order'] = False
        default['proformas'] = []
        return super(SaleOrder, self).copy(cr, uid, rec_id, default,
                                           context=context)

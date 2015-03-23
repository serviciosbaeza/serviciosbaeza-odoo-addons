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
        'quotation': fields.many2one(
            'sale.order', string="Quotation reference",
            help="This field indicates the quotation source for the proforma"),
        'proformas': fields.one2many('sale.order', 'quotation', "Proformas"),
    }

    def action_proforma(self, cr, uid, ids, context=None):
        wf_service = netsvc.LocalService("workflow")
        quotation = self.browse(cr, uid, ids[0], context=context)
        proforma = self.copy_data(
            cr, uid, ids[0], context=context,
            default={'origin': quotation.name,
                     'quotation': quotation.id,
                     'name': self.pool['ir.sequence'].next_by_code(
                         cr, uid, 'sale.order.proforma'),})
        # Remove reference of previous proformas
        del proforma['proformas']
        proforma_id = self.create(cr, uid, proforma, context=context)
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
        quotation = self.browse(cr, uid, ids[0], context=context)
        if quotation.proformas:
            act_window = {
                'type': 'ir.actions.act_window',
                'res_model': 'sale.order',
                'view_type': 'form',
                'domain': [('id', 'in', [x.id for x in quotation.proformas])]
            }
            if len(quotation.proformas) == 1:
                act_window['view_mode'] = 'form'
                act_window['res_id'] = quotation.proformas[0].id
            else:
                act_window['view_mode'] = 'tree,form'
            return act_window
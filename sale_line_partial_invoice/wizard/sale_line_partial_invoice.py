# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2012 Servicios Tecnológicos Avanzados (http://www.serviciosbaeza.com)
#                       Pedro Manuel Baeza <pedro.baeza@serviciosbaeza.com>
#    $Id$
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

from osv import fields, osv
from tools.translate import _
import netsvc
import sys

class sale_order_line_make_invoice(osv.osv_memory):
    _name = "sale.order.line.make.partial_invoice"
    _description = "Sale order line - Make partial invoice wizard"

    _columns = {
        'percentage': fields.float('Percentage (%)', digits=(16, 2), required=True),
    }

    def _get_percentage_ids(self, cr, ids, uid, context=None):
        """
        Get minimum value of uninvoiced percentage from given ids.
        @param ids: List of IDs for browsing uninvoiced quantities.
        """
        if len(ids):
            min_percentage = 1.0
            for order_line in self.pool.get('sale.order.line').browse(cr, uid, ids, context=context):
                uninvoiced_qty = order_line.product_uos_qty
                for invoice_line in order_line.invoice_lines:
                    if invoice_line.invoice_id.state not in ('draft', 'cancel'):
                        uninvoiced_qty -= invoice_line.quantity
                uninvoiced_percentage = uninvoiced_qty / order_line.product_uos_qty 
                if uninvoiced_percentage < min_percentage: min_percentage = uninvoiced_percentage
            return round(min_percentage, 2)
        return 1.0

    def _get_percentage(self, cr, uid, context=None) :
        """
        Get uninvoiced percentage from active ids. Used for default value. 
        """
        if not context is None:
            record_ids = context.get('active_ids', False)
            if record_ids:
                return self._get_percentage_ids(cr, record_ids, uid, context)
        return 1.0

    _defaults = {
        'percentage': _get_percentage,
    }

    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        """ Check pre-conditions.
        @param self: The object pointer.
        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param context: A standard dictionary 
        @return: New arch of view.
        """
        if context is None: context = {}
        active_ids = context.get('active_ids', False)
        if not len(active_ids):
            raise osv.except_osv(_('Warning'), _('No sale order line(s) selected'))
        ant_order_id = 0
        # Check for multiple sale orders
        for order_line in self.pool.get('sale.order.line').browse(cr, uid, active_ids, context):
            if ant_order_id:
                if order_line.order_id.id != ant_order_id:
                    raise osv.except_osv(_('Warning'), _('Partial invoice cannot be created for multiple sale orders'))         
            else:
                ant_order_id = order_line.order_id.id  
        if self._get_percentage_ids(cr, context.get('active_ids', False), uid, context=context) == 0.0:
            raise osv.except_osv(_('Warning'), _('Sale order line is fully invoiced!'))

        return super(sale_order_line_make_invoice, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar,submenu=False)
    
    def make_partial_invoice(self, cr, uid, ids, context=None):
        form = self.read(cr, uid, ids, [])[0]
        if form['percentage'] > self._get_percentage(cr, uid, context=context):
            raise osv.except_osv(_('Warning'), _("Selected percentage can't be greater than pending percentage"))
        
        def make_invoice(order, lines) :
            a = order.partner_id.property_account_receivable.id
            if order.partner_id and order.partner_id.property_payment_term.id:
                pay_term = order.partner_id.property_payment_term.id
            else:
                pay_term = False
            inv = {
                'name': order.name,
                'origin': order.name,
                'type': 'out_invoice',
                'reference': "P%dSO%d" % (order.partner_id.id, order.id),
                'account_id': a,
                'partner_id': order.partner_id.id,
                'address_invoice_id': order.partner_invoice_id.id,
                'address_contact_id': order.partner_invoice_id.id,
                'invoice_line': [(6, 0, lines)],
                'currency_id' : order.pricelist_id.currency_id.id,
                'comment': order.note,
                'payment_term': pay_term,
                'fiscal_position': order.fiscal_position.id or order.partner_id.property_account_position.id,
            }
            return self.pool.get('account.invoice').create(cr, uid, inv)
        
        order_line_obj = self.pool.get('sale.order.line')
        order_obj = self.pool.get('sale.order')
        order_lines_ids_to_invoice = {}
        invoiced_orders = set()
        order_line_ids = context.get('active_ids', [])
        #order_lines = order_line_obj.browse(cr, uid, context.get('active_ids', []), context=context)
        #for order_line in order_lines:
        for order_line_id in order_line_ids:
            if self._get_percentage_ids(cr, [order_line_id], uid) > 0:
            #if self._get_percentage_ids(self, cr, [order_line.id], uid) > 0:
                order_line = order_line_obj.browse(cr, uid, order_line_id, context=context)
                # Create invoice line
                temp_invoice_line_ids = order_line_obj.invoice_line_create(cr, uid, [order_line.id])
                if len(temp_invoice_line_ids):
                    invoice_line_id = temp_invoice_line_ids[0]
                    invoiced_orders.add(order_line.order_id)
                    if order_lines_ids_to_invoice.get(order_line.order_id):
                        order_lines_ids_to_invoice[order_line.order_id].append(invoice_line_id)
                    else:
                        order_lines_ids_to_invoice[order_line.order_id] = [invoice_line_id]
                    # Put correct quantity
                    self.pool.get('account.invoice.line').write(cr, uid, [invoice_line_id], { 'quantity': form['percentage'] * order_line.product_uos_qty })
                # Check invoiced flag condition (always must overwrite value)
                line_invoiced = (self._get_percentage_ids(cr, [order_line.id], uid, context = context) == 0)
                order_line_obj.write(cr, uid, [order_line.id], {'invoiced': line_invoiced})
        # Create invoice
        if len(order_lines_ids_to_invoice):
            #invoice_id = make_invoice(order_lines[0].order, order_lines_ids_to_invoice)
            invoice_ids = []
            # Fill many2many relation field
            for order in invoiced_orders:
                invoice_id = make_invoice(order, order_lines_ids_to_invoice[order])
                invoice_ids.append(invoice_id)
                cr.execute('INSERT INTO sale_order_invoice_rel \
                       (order_id,invoice_id) values (%s,%s)', (order.id, invoice_id))
                # Check if orders are completely invoiced
                flag = True
                for line in order.order_line:
                    if not line.invoiced:
                        flag = False
                        break
                if flag:
                    wf_service = netsvc.LocalService('workflow')
                    wf_service.trg_validate(uid, 'sale.order', order.id, 'all_lines', cr)
                    order_obj.write(cr, uid, [order.id], {'state': 'progress'})            
            
            # Return view with invoice(s) created
            if len(invoice_ids) == 1 :
                # Get view to show
                data_obj = self.pool.get('ir.model.data')
                result = data_obj._get_id(cr, uid, 'account', 'invoice_form')
                view_id = data_obj.browse(cr, uid, result).res_id
                return {
                    'domain': "[('id','=', " + str(invoice_ids[0]) + ")]",
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'account.invoice',
                    'context': context,
                    'res_id': invoice_ids[0],
                    'view_id': [view_id],
                    'type': 'ir.actions.act_window',
                    'nodestroy': False
                }
            
        return {}

sale_order_line_make_invoice()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

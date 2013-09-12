# -*- coding: utf-8 -*-
from openerp.osv import fields, orm
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT 
import datetime

class sale_order(orm.Model):

    def action_button_generate_agreement_invoicing(self, cr, uid, ids, context=None):
        agreement_ids = []
        agreement_obj = self.pool.get('account.periodical_invoicing.agreement')
        agreement_line_obj = self.pool.get('account.periodical_invoicing.agreement.line')
        for sale_order in self.browse(cr, uid, ids, context=context):
            agreement = { 'name': sale_order.name,
                          'partner_id': sale_order.partner_id.id,
                          'company_id': sale_order.company_id.id, 
                          'start_date': datetime.datetime.now().strftime(DEFAULT_SERVER_DATE_FORMAT), }
            agreement_id = agreement_obj.create(cr, uid, agreement, context=context)
            agreement_ids.append(agreement_id)
            for order_line in sale_order.order_line:
                agreement_line = { 'agreement_id': agreement_id,
                                   'product_id': order_line.product_id.id, 
                                   'discount': order_line.discount, 
                                   'quantity': order_line.product_uom_qty, }
                agreement_line_obj.create(cr, uid, agreement_line, context=context)
        if len(agreement_ids) == 1:
            # display the agreement record
            view_ref = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'account_periodical_invoicing', 'view_account_periodical_invocing_agreement_form')
            view_id = view_ref and view_ref[1] or False,
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'account.periodical_invoicing.agreement',
                'res_id': agreement_ids[0],
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': view_id,
                'target': 'current',
                'nodestroy': True,
            }
        else:
            return True

    _name = 'sale.order'
    _inherit = 'sale.order'

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

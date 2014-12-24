# -*- encoding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp.osv import orm
from openerp.tools.translate import _
from openerp import netsvc


class SaleOrder(orm.Model):
    _inherit = "sale.order"

    def button_draft(self, cr, uid, ids, context=None):
        wf_service = netsvc.LocalService("workflow")
        for order in self.browse(cr, uid, ids, context=context):
            if order.state != 'cancel':
                raise orm.except_orm(
                    _('Error'),
                    _("You can't back any order that it's not on cancel "
                      "state"))
            self.write(cr, uid, order.id, {'state': 'draft'}, context=context)
            # Remove and create again the workflow
            wf_service.trg_delete(uid, 'sale.order', order.id, cr)
            wf_service.trg_create(uid, 'sale.order', order.id, cr)
        return True

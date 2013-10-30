# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2013 Serv. Tecnol. Avanzados (http://www.serviciosbaeza.com)
#                       Pedro M. Baeza <pedro.baeza@serviciosbaeza.com> 
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
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
from openerp.osv import fields, orm
from openerp.tools.translate import _
from openerp import netsvc

class purchase_order_confirm(orm.TransientModel):
    """
    This wizard will confirm all the selected purchase orders.
    """

    _name = "purchase.order.confirm"
    _description = "Confirm the selected purchase orders"

    def order_confirm(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        wf_service = netsvc.LocalService('workflow')
        orders = self.pool.get('purchase.order').read(cr, uid,
                                                      context['active_ids'],
                                                      ['state', 'name'],
                                                      context=context)

        for record in orders:
            if not record['state'] == 'draft':
                raise orm.except_orm(_('Warning!'), 
                    _("Selected purchase order cannot be confirmed because it isn't in 'Draft' state: %s."
                      %record['name']))
            wf_service.trg_validate(uid, 'purchase.order', record['id'],
                                    'purchase_confirm', cr)
        return {'type': 'ir.actions.act_window_close'}
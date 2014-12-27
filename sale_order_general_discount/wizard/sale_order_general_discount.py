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

class sale_order_general_discount(osv.osv_memory):
    _name = "sale.order.general_discount"
    _description = "Sale order - General discount"

    _columns = {
        'discount': fields.float('Discount (%)', digits=(16, 2)),
    }

    def set_general_discount(self, cr, uid, ids, context=None):
        form = self.read(cr, uid, ids, [])[0]
        if form['discount'] > 100:
            raise osv.except_osv(_('Warning'), _("Discount can't be greater than 100%"))
        
        order = self.pool.get('sale.order').browse(cr, uid, context.get('active_id', []), context=context)
        order_lines_ids = []
        for order_line in order.order_line:
            order_lines_ids.append(order_line.id)
        if len(order_lines_ids):
            self.pool.get('sale.order.line').write(cr, uid, order_lines_ids, { 'discount': form['discount']})
        
        return {'type':'ir.actions.act_window_close' }

sale_order_general_discount()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

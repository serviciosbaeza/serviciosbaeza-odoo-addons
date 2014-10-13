# -*- coding: utf-8 -*-
##############################################################################
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################
from openerp.osv import fields, orm

class StockReportNoMoves(orm.TransientModel):
    _name = "stock.report.no_moves"

    _columns ={
        'date_from': fields.date('Date from'),
        'date_to': fields.date('Date to'),
    }

    def button_show_products(self, cr, uid, ids, data, context=None):
        move_obj = self.pool['stock.move']
        product_obj = self.pool['product.product']
        form = self.browse(cr, uid, ids[0], context=context)
        product_ids = product_obj.search(cr, uid, [], context=context)
        date_from = form.date_from
        date_to = form.date_to
        products_wo_moves = []
        for product_id in product_ids:
            move_ids = move_obj.search(cr, uid,
                                       [('product_id', '=', product_id),
                                        ('date', '>=', date_from),
                                        ('date', '<=', date_to)],
                                       context=context)
            if not move_ids:
                products_wo_moves.append(product_id)
        # Return product list
        return {
            'domain': "[('id', 'in', %s)]" % products_wo_moves,
            'view_type': 'form',
            'view_mode': 'list,form',
            'res_model': 'product.product',
            'context': context,
            'type': 'ir.actions.act_window',
            'nodestroy': True,
        }

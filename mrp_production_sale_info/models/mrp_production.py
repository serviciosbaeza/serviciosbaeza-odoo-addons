# -*- encoding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################

from openerp.osv import orm, fields


class MrpProduction(orm.Model):
    _inherit = 'mrp.production'

    def _get_sale_info(self, cr, uid, ids, name, arg, context=None):
        res = {}
        procurement_obj = self.pool['procurement.order']
        sale_line_obj = self.pool['sale.order.line']
        for record in self.browse(cr, uid, ids, context=context):
            res[record.id] = {
                'partner': False,
                'sale_order': False,
                'sale_line': False,
            }
            procurement_ids = procurement_obj.search(
                cr, uid, [('production_id', '=', record.id)], context=context)
            if not procurement_ids:
                continue
            line_ids = sale_line_obj.search(
                cr, uid, [('procurement_id', 'in', procurement_ids)],
                context=context)
            if not line_ids:
                continue
            line = sale_line_obj.browse(
                cr, uid, line_ids[0], context=context)
            res[record.id] = {
                'partner': (line.order_id.partner_id and
                            line.order_id.partner_id.id or False),
                'sale_order': line.order_id.id,
                'sale_line': line.id,
            }
        return res

    def _sale_order_search(self, cr, uid, obj, name, args, context=None):
        field, operator, value = args[0]
        order_obj = self.pool['sale.order']
        order_line_obj = self.pool['sale.order.line']
        if isinstance(value, (int, long)):
            field = 'id'
        else:
            field = 'name'
        order_ids = order_obj.search(
            cr, uid, [(field, operator, value)], context=context)
        order_line_ids = order_line_obj.search(
            cr, uid, [('order_id', 'in', order_ids)], context=context)
        procurements = [x.procurement_id for x in order_line_obj.browse(
            cr, uid, order_line_ids, context=context)]
        prod_ids = [x.production_id.id for x in procurements
                    if x.production_id]
        return [('id', 'in', prod_ids)]

    _columns = {
        'partner': fields.function(
            _get_sale_info, type="many2one", relation='res.partner',
            string='Customer', multi=True),
        'sale_order': fields.function(
            _get_sale_info, type="many2one", relation='sale.order',
            string='Sale Order', multi=True, fnct_search=_sale_order_search),
        'sale_line': fields.function(
            _get_sale_info, type="many2one", relation='sale.order.line',
            string='Sale Line', multi=True),
    }

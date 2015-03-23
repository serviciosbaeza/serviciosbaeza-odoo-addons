# -*- encoding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp.osv import orm


class ProcurementOrder(orm.Model):
    _inherit = 'procurement.order'

    def write(self, cr, uid, ids, vals, context=None):
        if vals.get('production_id'):
            production = self.pool['mrp.production'].browse(
                cr, uid, vals['production_id'], context=context)
            production.write({'no_confirm': True})
        return super(ProcurementOrder, self).write(
            cr, uid, ids, vals, context=context)

    def make_mo(self, cr, uid, ids, context=None):
        res = super(ProcurementOrder, self).make_mo(
            cr, uid, ids, context=context)
        for procurement in self.browse(cr, uid, ids, context=context):
            if (procurement.production_id and
                    procurement.production_id.no_confirm):
                procurement.production_id.write({'no_confirm': False})
        return res

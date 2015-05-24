# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2014 Serv. Tecnol. Avanzados (http://www.serviciosbaeza.com)
#                       Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
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
from openerp.osv import orm


class ProductPricelist(orm.Model):
    _inherit = "product.pricelist"

    def price_get_multi(self, cr, uid, pricelist_ids,
                        products_by_qty_by_partner, context=None):
        results = super(ProductPricelist, self).price_get_multi(
            cr, uid, pricelist_ids, products_by_qty_by_partner,
            context=context)
        if not results.get('item_id'):
            return results
        product_obj = self.pool['product.product']
        pl_item_obj = self.pool['product.pricelist.item']
        supplierinfo_obj = self.pool['product.supplierinfo']
        pl_pinfo_obj = self.pool['pricelist.partnerinfo']
        product_uom_obj = self.pool['product.uom']
        pl_item = pl_item_obj.browse(cr, uid, results['item_id'],
                                     context=context)
        if pl_item.base != -2:
            return results  # Price is not based on supplier info
        for product_id in results.keys():
            if product_id == 'item_id':
                continue
            product = product_obj.read(
                cr, uid, product_id, ['product_tmpl_id', 'uom_id'],
                context=context)
            from_uom = context.get('uom') or product['uom_id'][0]
            tmpl_id = product['product_tmpl_id'][0]
            for src_product_id, qty, partner_id in products_by_qty_by_partner:
                # Match product in the query tuple
                if src_product_id != product_id:
                    continue
                qty_in_product_uom = qty
                for pricelist_id in results[product_id].keys():
                    sinfo_ids = supplierinfo_obj.search(
                        cr, uid, [('product_id', '=', tmpl_id),
                                  ('name', '=', partner_id)], context=context)
                    if not sinfo_ids:
                        continue
                    sinfo = supplierinfo_obj.browse(
                        cr, uid, sinfo_ids[0], context=context)
                    seller_uom = sinfo.product_uom.id or False
                    if seller_uom and from_uom and from_uom != seller_uom:
                        qty_in_product_uom = product_uom_obj._compute_qty(
                            cr, uid, from_uom, qty, to_uom_id=seller_uom)
                    pl_pinfo_ids = pl_pinfo_obj.search(
                        cr, uid, [('suppinfo_id', 'in', sinfo_ids)],
                        order="min_quantity desc")
                    for pl_pinfo in pl_pinfo_obj.read(
                            cr, uid, pl_pinfo_ids,
                            ['discount', 'min_quantity']):
                        if pl_pinfo['quantity'] <= qty_in_product_uom:
                            price = results[product_id][pricelist_id]
                            results[product_id][pricelist_id] = (
                                price * (1 - pl_pinfo['discount'] * 0.01))
                        else:
                            break
                    break
        return results

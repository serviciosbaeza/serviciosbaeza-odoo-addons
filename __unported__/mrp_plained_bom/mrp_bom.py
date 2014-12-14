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

class mrp_bom(orm.Model):
    _inherit = "mrp.bom"

    def _get_plained_qty(self, cr, uid, ids, name, arg, context=None):
        result = {}
        bom_id = context and context.get('active_id', False) or False
        if (not context.get('active_model', False) or
                context['active_model'] != 'mrp.bom'):
            return result
        bom_parent = self.browse(cr, uid, bom_id, context=context)

        def addChildQty(product_id, multiplier, bom_lines):
            if not bom_lines:
                return 0
            else:
                qty = 0
                for bom in bom_lines:
                    if product_id == bom.product_id.id:
                        qty += multiplier * bom.product_qty
                    sids = self.search(cr, uid, [
                                       ('bom_id', '=', False),
                                       ('product_id', '=', bom.product_id.id)
                                       ])
                    for bom2 in self.browse(cr, uid, sids):
                        qty += addChildQty(product_id,
                                           multiplier * bom.product_qty,
                                           bom2.bom_lines)
                return qty

        for bom in self.browse(cr, uid, ids, context=context):
            if bom.id == bom_id:
                result[bom.id] = bom.product_qty
            else:
                result[bom.id] = addChildQty(bom.product_id.id, 1,
                                             bom_parent.bom_lines)
        return result

    def _plained_child_compute(self, cr, uid, ids, name, arg, context=None):
        """
        Gets BoMs ids unfolded for all descendants. When a product is
        duplicated across BoM, only first BoM occurrence is added. This is to 
        allow the calculation of the special field _get_plained_quantity.
        @param self: The object pointer
        @param cr: The current row, from the database cursor,
        @param uid: The current user ID for security checks
        @param ids: List of selected IDs
        @param name: Name of the field
        @param arg: User defined argument
        @param context: A standard dictionary for contextual values
        @return: Dictionary of values
        """
        result = {}
        if context is None:
            context = {}
        bom_id = context and context.get('active_id', False) or False
        if bom_id in ids:
            # Include only parent level
            def addMaterialsRecursive(components, products, bom_lines):
                if not bom_lines:
                    return components
                else:
                    for bom in bom_lines:
                        if not bom.product_id.id in products:
                            products.append(bom.product_id.id)
                            components.append(bom.id)
                    product_ids = map(lambda x: x.product_id.id, bom_lines)
                    sids = self.search(cr, uid, [
                                       ('bom_id', '=', False),
                                       ('product_id', 'in', product_ids)
                                       ])
                    for bom in self.browse(cr, uid, sids):
                        addMaterialsRecursive(components, products, bom.bom_lines)

            bom_parent = self.browse(cr, uid, bom_id, context=context)
            components = []
            products = []
            addMaterialsRecursive(components, products, bom_parent.bom_lines)
            result[bom_id] = components
        return result

    _columns = {
        'child_plained_ids': fields.function(_plained_child_compute,
                                             relation='mrp.bom',
                                             string="Plained BoM Hierarchy",
                                             type='many2many'),
        'plained_qty': fields.function(_get_plained_qty,
                                       string="Plained quantity",
                                       type='float'),
    }

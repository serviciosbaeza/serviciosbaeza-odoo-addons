# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2013 Serv. Tecnol. Avanzados (http://www.serviciosbaeza.com)
#                       Pedro M. Baeza <pedro.baeza@serviciosbaeza.com> 
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

class product_category(orm.Model):
    _inherit = "product.category"

    def name_search(self, cr, uid, name, args=None, operator='ilike',
                      context=None, limit=100):
        if not args:
            args = []
        args = args[:]
        ids = []
        if name:
            # Get children categories with that name
            ids = self.search(cr, uid, [('name', operator, name)] + args,
                              context=context, limit=limit)
            # Search for any category that contains the name, and add their
            # children that match args
            parent_ids = self.search(cr, uid, [('name', operator, name)],
                                     context=context, limit=limit)
            if parent_ids:
                ids2 = self.search(cr, uid, [('parent_id', 'child_of',
                                              parent_ids)] + args,
                                   context=context, limit=limit)
                ids += ids2
        else:
            ids = self.search(cr, uid, args, context=context, limit=limit)
        if ids:
            return self.name_get(cr, uid, ids, context=context)
        else:
            return []

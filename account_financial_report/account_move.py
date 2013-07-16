# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    Copyright (c) 2009 Zikzakmedia S.L. (http://zikzakmedia.com) All Rights Reserved.
#                       Jordi Esteve <jesteve@zikzakmedia.com>
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import netsvc
import pooler
from osv import fields, osv
from tools.translate import _

import sys
class account_move(osv.osv):
    _inherit = "account.move"

    def _name_split(self, cr, uid, ids, name, args, context=None):
        if context is None:
            context = {}
        result = {}
        for move in self.browse(cr, uid, ids, context):
           if len(move.name) > 8:
               result[move.id] = move.name.replace('-','- ').replace('/','/ ')
           else:
               result[move.id] = move.name
        return result

    _columns = {
       'name_split' : fields.function(_name_split, method=True, type='char', string="Number", help="inserts space for wrap in longer numbers"),
    }
account_move()

class account_move_line(osv.osv):
    _inherit = "account.move.line"

    def _name_split(self, cr, uid, ids, name, args, context=None):
        if context is None:
            context = {}
        result = {}
        for move in self.browse(cr, uid, ids, context):
           if len(move.name) > 8:
               result[move.id] = move.name.replace('-','- ').replace('/','/ ')
           else:
               result[move.id] = move.name
        return result

    _columns = {
       'name_split' : fields.function(_name_split, method=True, type='char', string="Number", help="inserts space for wrap in longer numbers"),
    }
account_move_line()

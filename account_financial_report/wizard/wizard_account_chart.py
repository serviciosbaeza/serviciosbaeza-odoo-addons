# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2009 Zikzakmedia S.L. (http://zikzakmedia.com) All Rights Reserved.
#                       Jordi Esteve <jesteve@zikzakmedia.com>
#    Copyright (C) 2012 Pexego Sistemas Informáticos. All Rights Reserved
#                       $Marta Vázquez Rodríguez$
#                       $Omar Castiñeira Saavedra$
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


from osv import osv, fields
class account_account_chart_report(osv.osv_memory):
    _name = "account.account.chart.report"
    _description = "Chart of accounts"
    _columns = {
        'account':fields.many2one('account.account', 'Account', required=True)
    }
    def print_report(self, cr, uid, ids, context=None):
        """prints report"""
        if context is None:
            context = {}

        data = self.read(cr, uid, ids)[0]
        datas = {
             'ids': context.get('active_ids',[]),
             'model': 'ir.ui.menu',
             'form': data
        }

        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'account.account.chart.report.wzd',
            'datas': datas
            }


account_account_chart_report()



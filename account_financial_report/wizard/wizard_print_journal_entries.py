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

from tools.translate import _
from osv import osv, fields

class account_journal_entries_report(osv.osv_memory):
    _name = "account.journal.entries.report"
    _description = "Print journal by entries"
    _columns = {
        'journal_ids': fields.many2many('account.journal', 'account_journal_entries_journal_rel', 'acc_journal_entries_id','journal_id','Journal', required=True),
        'period_ids': fields.many2many('account.period','account_journal_entries_account_period_rel','acc_journal_entries_id','account_period_id','Period'),
        'sort_selection': fields.selection([
                   ('date','By date'),
                   ("to_number(name,'999999999')",'By entry number'),
                   ('ref','By reference number')],'Entries Sorted By', required=True),
        'landscape': fields.boolean('Landscape mode')
    }
    def default_get(self, cr, uid, fields, context=None):
        if context is None: context = {}
        res = {}
        res['sort_selection'] = 'date'
        res['journal_ids'] = self.pool.get('account.journal').search(cr,uid, [])
        res['period_ids'] = self.pool.get('account.period').search(cr, uid, [('fiscalyear_id', '=', self.pool.get('account.fiscalyear').find(cr, uid))])
        return res
    
    def _check_data(self, cr, uid, ids, context=None):
        if ids:
            current_obj = self.browse(cr, uid, ids[0], context=context)
            if current_obj.period_ids and current_obj.journal_ids:
                period_id =  current_obj.period_ids[0].id
                journal_id = current_obj.journal_ids[0].id
                if type(period_id)==type([]):
                    ids_final = []
                    for journal in journal_id:
                        for period in period_id:
                            ids_journal_period = self.pool.get('account.journal.period').search(cr,uid, [('journal_id','=',journal),('period_id','=',period)])

                            if ids_journal_period:
                                ids_final.append(ids_journal_period)

                    if not ids_final:
                        raise osv.except_osv(_('No Data Available'), _('No records found for your selection!'))
        return True
    
    def _check(self, cr, uid, ids, context=None):
         if ids:
            current_obj = self.browse(cr, uid, ids[0], context=context)
            if current_obj.landscape==True:
                return 'report_landscape'
            else:
                return 'report'

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
        if self._check_data(cr, uid, ids, context=context):
            if self._check(cr, uid, ids, context=context) == 'report_landscape':
                return {
                    'type': 'ir.actions.report.xml',
                    'report_name': 'account.journal.entries.report.wzd1',
                    'datas': datas
                    }
            else:
                return {
                    'type': 'ir.actions.report.xml',
                    'report_name': 'account.journal.entries.report.wzd',
                    'datas': datas
                    }

account_journal_entries_report()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:


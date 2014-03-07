# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution	
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
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
import time
from tools.translate import _
class account_general_ledger_cumulative_report(osv.osv_memory):
    _name = "account.general.ledger.cumulative.report"
    _description = "Cumulative general ledger"
    _columns = {
        'account_list': fields.many2many('account.account', 'account_gene_ledger_account_list_rel', 'acc_gen_ledger_id','account_id','Account', required=True),
        'company_id': fields.many2one('res.company', 'Company', required=True),
        'state': fields.selection([
                    ('bydate','By Date'),
                    ('byperiod','By Period'),
                    ('all', 'By Date and Period'),
                    ('none','No Filter')],'Date/Period Filter'),
        'fiscalyear': fields.many2one('account.fiscalyear', 'Fiscal year', help='Keep empty for all open fiscal year'),
        'period_ids': fields.many2many('account.period','account_gene_ledger_account_period_rel','acc_gen_ledger_id','account_period_id','Periods',help='All periods if empty'),
        'sortbydate': fields.selection([
                   ('sort_date','Date'),
                   ('sort_mvt','Movement')],'Sort By', required=True),
        'display_account': fields.selection([
                    ('bal_all','All'),
                    ('bal_solde', 'With balance is not equal to 0'),
                    ('bal_mouvement','With movements')], 'Display accounts'),
        'landscape': fields.boolean('Landscape mode'),
        'initial_balance': fields.boolean('Show initial balances'),
        'amount_currency': fields.boolean('With Currency'),
        'date_from': fields.date('Start date', required=True),
        'date_to': fields.date('End date', required=True),
        'moment_form': fields.selection([
                    ('checkreport', 'Check report'),
                    ('report_landscape','Report landscape'),
                    ('report','Report'),],'Time is the form'),
    }
#    ('checktype','Check type'),
#                    ('account_selection','Account selection'),
    def default_get(self, cr, uid, fields, context=None):
        if context is None: context = {}
        res = {}
        result = []
        if context and context.get('active_model') == 'account.account':
            list_ids = context.get('active_ids',[])
            if list_ids:
                res['account_list'] = [(6,0,list_ids)]
        res['company_id'] = self.pool.get('res.users').browse(cr, uid, uid, context).company_id.id
        res['fiscalyear'] = self.pool.get('account.fiscalyear').find(cr, uid)
        res['context'] = context
        res['date_from'] = time.strftime('%Y-01-01')
        res['date_to'] = time.strftime('%Y-%m-%d')
        
        return res

    def _check(self, cr, uid, ids, context=None):
        if ids:
            current_obj = self.browse(cr, uid, ids[0], context=context)
            if current_obj.landscape==True:
                return 'report_landscape'
        else:
            return 'report'

    def _check_date(self, cr, uid, ids, context=None):
        if ids:
            current_obj = self.browse(cr, uid, ids[0], context=context)
            res = self.pool.get('account.fiscalyear').search(cr, uid, [('date_start', '<=', current_obj.date_from),('date_stop', '>=', current_obj.date_from)])
            if res:
                acc_fy = self.pool.get('account.fiscalyear').browse(cr, uid, res[0], context=context)
                if current_obj.date_to > acc_fy.date_stop or current_obj.date_to < acc_fy.date_start:
                    raise osv.except_osv(_('UserError'),_('Date to must be set between %s and %s') % (acc_fy.date_start,acc_fy.date_stop))
                else:
                    return 'checkreport'
            else:
                raise osv.except_osv(_('UserError'),_('Date not in a defined fiscal year'))

    def _check_state(self, cr, uid, ids, context=None):
        if ids:
            current_obj = self.browse(cr, uid, ids[0], context=context)
            if current_obj.state == 'bydate':
                self._check_date(cr, uid, ids, context=context)
   
        return True


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
        
        if self._check(cr, uid, ids, context=context) == 'report_landscape':
            if self._check_state(cr, uid, ids, context=context):
                return {
                'type': 'ir.actions.report.xml',
                'report_name': 'account.general.ledger.cumulative.report.wzd1',
                'datas': datas
                }
        else:
            if self._check_state(cr, uid, ids, context=context):
                return {
                'type': 'ir.actions.report.xml',
                'report_name': 'account.general.ledger.cumulative.report.wzd',
                'datas': datas
                }

    
account_general_ledger_cumulative_report()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
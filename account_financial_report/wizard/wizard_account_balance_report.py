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

import time
from tools.translate import _
from osv import osv, fields

class account_balance_full_report(osv.osv_memory):
    _name = "account.balance.full.report"
    _description = "Print Full account balance"
    _columns = {
        'company_id': fields.many2one('res.company', 'Company', required=True),
        'account_list': fields.many2many('account.account', 'account_balance_account_list_rel', 'acc_balance_id','account_id','Root accounts', required=True),
        'state': fields.selection([
                    ('bydate','By Date'),
                    ('byperiod','By Period'),
                    ('all', 'By Date and Period'),
                    ('none','No Filter')],'Date/Period Filter'),
        'fiscalyear': fields.many2one('account.fiscalyear', 'Fiscal year', help='Keep empty to use all open fiscal years to compute the balance'),
        'periods': fields.many2many('account.period','account_balance_account_period_rel','acc_balance_id','account_period_id','Periods', help='All periods in the fiscal year if empty'),
        'display_account': fields.selection([
                    ('bal_all','All'),
                    ('bal_solde', 'With balance'),
                    ('bal_mouvement','With movements')], 'Display accounts'),
        'display_account_level': fields.integer('Up to level', help= 'Display accounts up to this level (0 to show all)'),
        'date_from': fields.date('Start date'),
        'date_to': fields.date('End date')
    }

    def default_get(self, cr, uid, fields, context=None):
        if context is None: context = {}
        res = {}
        result = []
        if context and context.get('active_model') == 'account.account':
            list_ids = context.get('active_ids',[])
            if list_ids:
                res['account_list'] = [(6,0,list_ids)]
        res['state'] = 'none'
        res['display_account_level'] = 0
        res['date_from'] = time.strftime('%Y-01-01')
        res['date_to'] = time.strftime('%Y-%m-%d')
        res['company_id'] = self.pool.get('res.users').browse(cr, uid, uid, context).company_id.id
        res['fiscalyear'] = self.pool.get('account.fiscalyear').find(cr, uid)
        return res

    def _check_state(self, cr, uid, ids, context=None):
        if ids:
            current_obj = self.browse(cr, uid, ids[0], context=context)
            if current_obj.state and current_obj.state == 'bydate':
                self._check_date(cr, uid, ids, context=context)
        return True

    def _check_date(self, cr, uid, ids, context=None):
        if ids:
            current_obj = self.browse(cr, uid, ids[0], context=context)
            res = self.pool.get('account.fiscalyear').search(cr, uid, [('date_start', '<=', current_obj.date_from),('date_stop', '>=', current_obj.date_from)])
            if res:
                acc_fy = self.pool.get('account.fiscalyear').browse(cr, uid, res[0], context=context)
                if current_obj.date_to > acc_fy.date_stop or current_obj.date_to < acc_fy.date_start:
                    raise osv.except_osv(_('UserError'),_('Date to must be set between %s and %s') % (acc_fy.date_start,acc_fy.date_stop))
                else:
                    return True
            else:
                raise osv.except_osv(_('UserError'),_('Date not in a defined fiscal year'))

    def print_report(self, cr, uid, ids, context=None):
        """prints report"""
        if context is None:
            context = {}

        data = self.read(cr, uid, ids)[0]
        datas = {
             'ids': context.get('active_ids',[]),
             'model': 'account.balance.full.report',
             'form': data
        }
        self._check_state(cr, uid, ids, context=context)
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'account.balance.full.report.wzd',
            'datas': datas
            }

account_balance_full_report()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:





     
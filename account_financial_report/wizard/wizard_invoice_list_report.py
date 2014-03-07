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
from osv import osv, fields

class account_invoice_list_report(osv.osv_memory):
    _name = "account.invoice.list.report"
    _description = "Print invoice list"
    _columns = {
        'company_id': fields.many2one('res.company','Company', required=True),
        'out_invoice': fields.boolean('Customer invoices'),
        'out_refund': fields.boolean('Customer refunds'),
        'in_invoice': fields.boolean('Supplier invoices'),
        'in_refund': fields.boolean('Supplier refunds'),
        'draft': fields.boolean('Draft'),
        'proforma': fields.boolean('Pro-forma'),
        'open': fields.boolean('Open'),
        'paid': fields.boolean('Done'),
        'cancel': fields.boolean('Cancelled'),
        'detailed_taxes': fields.boolean('Detailed taxes'),
        'state': fields.selection([
                    ('bydate','By Date'),
                    ('byperiod','By Period'),
                    ('all', 'By Date and Period'),
                    ('none','No Filter')],'Date/Period Filter'),
        'periods': fields.many2many('account.period','account_invoice_list_account_period_rel','acc_inv_list_id','account_period_id','Periods',help='All periods if empty'),
        'date_from': fields.date('Start date', required=True),
        'date_to': fields.date('End date', required=True),
        'order_by': fields.selection([
                    ('number','Number'),
                    ('date','Date'),
                    ('partner','Partner')],'Order by'),
    }
    def default_get(self, cr, uid, fields, context=None):
        if context is None: context = {}
        res = {}
        res['company_id'] = self.pool.get('res.users').browse(cr, uid, uid, context).company_id.id
        res['context'] = context
        res['date_from'] = time.strftime('%Y-01-01')
        res['date_to'] = time.strftime('%Y-%m-%d')
        res['out_invoice'] = True
        res['out_refund'] = True
        res['in_invoice'] = True
        res['in_refund'] = True
        res['open'] = True
        res['paid'] = True
        res['state'] = 'none'
        res['order_by'] = 'number'

        return res

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
        'report_name': 'account.invoice.list.report.wzd',
        'datas': datas
        }



account_invoice_list_report()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

  

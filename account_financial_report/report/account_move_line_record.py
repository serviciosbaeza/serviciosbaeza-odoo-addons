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


import time
from report import report_sxw

#
# Use period and Journal for selection of resources
#
class journal_print(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(journal_print, self).__init__(cr, uid, name, context)
        self.localcontext.update( {
            'time': time,
        })

    def set_context(self, objects, data, ids, report_type = None):
        if data['model'] == 'ir.ui.menu':
            period_ids = data['form']['period_ids']
            journal_ids = data['form']['journal_ids']
            move_ids = self.pool.get('account.move').search(self.cr, self.uid, [('period_id', 'in', period_ids),('journal_id', 'in', journal_ids),('state', '<>', 'draft')],order=data['form']['sort_selection']+',id')

        else:
            move_ids = []
            journalperiods = self.pool.get('account.journal.period').browse(self.cr, self.uid, ids)
            for jp in journalperiods:
                move_ids = self.pool.get('account.move').search(self.cr, self.uid, [('period_id', '=', jp.period_id.id),('journal_id', '=', jp.journal_id.id),('state', '<>', 'draft')],order='date,id')
        
        objects = self.pool.get('account.move').browse(self.cr, self.uid, move_ids)
        super(journal_print, self).set_context(objects, data, ids, report_type)


report_sxw.report_sxw('report.account.journal.entries.report.wzd', 'account.journal.period', 'addons/account_financial_report/report/account_move_line_record.rml', parser=journal_print, header=False)
report_sxw.report_sxw('report.account.journal.entries.report.wzd1', 'account.journal.period', 'addons/account_financial_report/report/account_move_line_record_h.rml', parser=journal_print, header=False)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:


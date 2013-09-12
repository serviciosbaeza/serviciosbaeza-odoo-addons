# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2012 Serv. Tecnol. Avanzados (http://www.serviciosbaeza.com) All Rights Reserved.
#                       Pedro M. Baeza <pedro.baeza@serviciosbaeza.com> 
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
from tools.translate import _
import time

class renew_wizard(osv.osv_memory):

    _name = "account.periodical_invoicing.renew_wizard"

    def _get_renovation_date(self, cr, uid, context=None):
        """
        It returns the next expiration date of the active agreement.
        @rtype: string with date
        @return: Next expiration date of the agreement.
        """
        agreements = self.pool.get('account.periodical_invoicing.agreement').browse(cr, uid, context.get('active_ids',[]), context=context)
        return agreements[0].next_expiration_date

    _columns = {
        'date': fields.date('Renewal date', help="Effective date of the renewal. This date is the one taken into account in the next renewal", required=True),
        'comments': fields.char('Comments', size=200, help='Renewal comments'),
    }

    _defaults = {
        'date': _get_renovation_date,
    }
    
    def create_renewal(self, cr, uid, ids, context=None):
        """
        It creates agreement renewal records with data given in this wizard.
        """
        if context is None: context = {}
        
        # Create agreement renewal record
        renew_wizard = self.browse(cr, uid, ids[0], context=context)
        agreement_ids = context.get('active_ids',[])
        for agreement_id in agreement_ids:
            self.pool.get('account.periodical_invoicing.agreement.renewal').create(cr, uid, {
                'agreement_id': agreement_id,
                'date': renew_wizard.date,
                'comments': renew_wizard.comments,
            }, context=context)
        
        # Change last renovation date and state in agreement
        self.pool.get('account.periodical_invoicing.agreement').write(cr, uid, agreement_ids, { 'last_renovation_date': renew_wizard.date, 'renewal_state': 'renewed' }, context=context)
                    
        return {'type': 'ir.actions.act_window_close'}

renew_wizard()

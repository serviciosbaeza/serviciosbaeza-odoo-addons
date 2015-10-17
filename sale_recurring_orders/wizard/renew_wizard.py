# -*- coding: utf-8 -*-
# (c) 2013-2015 Serv. Tecnol. Avanzados - Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, fields, api


class RenewWizard(models.TransientModel):
    _name = "sale.recurring_orders.renew_wizard"

    def _get_renewal_date(self):
        """It returns the next expiration date of the active agreement.
        @rtype: string with date
        @return: Next expiration date of the agreement.
        """
        agreements = self.env['sale.recurring_orders.agreement'].browse(
            self.env.context.get('active_ids', []))
        return agreements[:1].next_expiration_date

    date = fields.Date(
        string='Renewal date', required=True,
        help="Effective date of the renewal. This date is the one taken into "
             "account in the next renewal",
        default=_get_renewal_date)
    comments = fields.Char(
        string='Comments', size=200, help='Renewal comments')

    @api.multi
    def create_renewal(self, cr, uid, ids, context=None):
        """It creates agreement renewal records with data given in this wizard.
        """
        self.ensure_one()
        agreement_ids = context.get('active_ids', [])
        for agreement_id in agreement_ids:
            self.env['sale.recurring_orders.agreement.renewal'].create(
                {'agreement_id': agreement_id,
                 'date': self.date,
                 'comments': self.comments})
        # Change last renovation date and state in agreement
        agreement_model = self.env['sale.recurring_orders.agreement']
        agreement_model.browse(agreement_ids).write(
            {'last_renovation_date': self.date,
             'renewal_state': 'renewed'})
        return True

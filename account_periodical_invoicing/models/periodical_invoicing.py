# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2012 Serv. Tecnol. Avanzados (http://www.serviciosbaeza.com)
#                       Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
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
from openerp import models, fields, api, _
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from collections import OrderedDict
import datetime
import openerp.addons.decimal_precision as dp


class Agreement(models.Model):
    _name = 'account.periodical_invoicing.agreement'
    _inherit = 'mail.thread'
    _description = "Periodical invoicing agreement"

    def _get_next_term_date(self, date, unit, interval):
        """Get the date that results on incrementing given date an interval of
        time in time unit.
        @param date: Original date.
        @param unit: Interval time unit.
        @param interval: Quantity of the time unit.
        @rtype: date
        @return: The date incremented in 'interval' units of 'unit'.
        """
        if unit == 'days':
            return date + timedelta(days=interval)
        elif unit == 'weeks':
            return date + timedelta(weeks=interval)
        elif unit == 'months':
            return date + relativedelta(months=interval)
        elif unit == 'years':
            return date + relativedelta(years=interval)

    def _get_previous_term_date(self, date, unit, interval):
        """Get the date that results on decrementing given date an interval of
        time in time unit.
        @param date: Original date.
        @param unit: Interval time unit.
        @param interval: Quantity of the time unit.
        @rtype: date
        @return: The date decremented in 'interval' units of 'unit'.
        """
        if unit == 'days':
            return date - timedelta(days=interval)
        elif unit == 'weeks':
            return date - timedelta(weeks=interval)
        elif unit == 'months':
            return date - relativedelta(months=interval)
        elif unit == 'years':
            return date - relativedelta(years=interval)

    @api.multi
    def _get_next_expiration_date(self):
        """Get next expiration date of the agreement. For unlimited agreements,
        get max date
        """
        for agreement in self:
            if agreement.prolong == 'fixed':
                agreement.next_expiration_date = agreement.end_date
            elif agreement.prolong == 'unlimited':
                today = datetime.date.today()
                date = self._get_next_term_date(
                    fields.Date.from_string(agreement.start_date),
                    agreement.prolong_unit, agreement.prolong_interval)
                while date < today:
                    date = self._get_next_term_date(
                        date, agreement.prolong_unit,
                        agreement.prolong_interval)
                agreement.next_expiration_date = date
            else:
                # for renewable fixed term
                agreement.next_expiration_date = self._get_next_term_date(
                    fields.Date.to_string(agreement.last_renovation_date or
                                          agreement.start_date),
                    agreement.prolong_unit, agreement.prolong_interval)

    def _get_default_currency_id(self):
        company_obj = self.env['res.company']
        company_id = company_obj._company_default_get(
            'account.periodical_invoicing.agreement')
        company = company_obj.browse(company_id)
        return company.currency_id

    name = fields.Char(
        'Name', index=True, required=True,
        help='Name that helps to identify the agreement')
    number = fields.Char(
        'Agreement number', select=1, size=32,
        help="Number of agreement. Keep empty to get the number "
             "assigned by a sequence.")
    active = fields.Boolean(
        string='Active', default=True,
        help='Unchecking this field, quotas are not generated')
    partner_id = fields.Many2one(
        'res.partner', 'Customer', select=1, change_default=True,
        required=True, help="Customer you are making the agreement with")
    company_id = fields.Many2one(
        'res.company', 'Company', required=True,
        help="Company that signs the agreement",
        default=lambda self: self.env['res.company']._company_default_get(
            'account.periodical_invoicing.agreement'))
    start_date = fields.Date(
        'Start date', index=True,
        help="Beginning of the agreement. Keep empty to use the current date")
    prolong = fields.Selection(
        [('recurrent', 'Renewable fixed term'),
         ('unlimited', 'Unlimited term'),
         ('fixed', 'Fixed term')], string='Prolongation', default='unlimited',
        help="Sets the term of the agreement. 'Renewable fixed term': It "
             "sets a fixed term, but with possibility of manual renew; "
             "'Unlimited term': Renew is made automatically; 'Fixed "
             "term': The term is fixed and there is no possibility to "
             "renew.")
    end_date = fields.Date('End date', help="End date of the agreement")
    prolong_interval = fields.Integer(
        string='Interval', default=1,
        help="Interval in time units to prolong the agreement until new "
             "renewall (that is automatic for unlimited term, manual for "
             "renewable fixed term).")
    prolong_unit = fields.Selection(
        [('days', 'days'),
         ('weeks', 'weeks'),
         ('months', 'months'),
         ('years', 'years')], string='Interval unit', default='years',
        help='Time unit for the prolongation interval')
    agreement_line = fields.One2many(
        'account.periodical_invoicing.agreement.line', 'agreement_id',
        'Agreement lines')
    invoice_line = fields.One2many(
        'account.periodical_invoicing.agreement.invoice', 'agreement_id',
        'Invoice lines', readonly=True)
    renewal_line = fields.One2many(
        'account.periodical_invoicing.agreement.renewal', 'agreement_id',
        string='Renewal lines', readonly=True)
    last_renovation_date = fields.Date(
        string='Last renovation date',
        help="Last date when agreement was renewed (same as start date if "
             "not renewed)")
    next_expiration_date = fields.Date(
        compute="_get_next_expiration_date", string='Next expiration date',
        store=True)
    period_type = fields.Selection(
        selection=[('pre-paid', 'Pre-paid'),
                   ('post-paid', 'Post-paid')],
        string="Period type", required=True, default='pre-paid',
        help="Period type for invoicing. 'Pre-paid': Invoices are "
             "generated for the upcoming period. 'Post-paid': Invoices "
             "are generated for the consumed period.")
    # TODO: Añadir seguimiento al generar una factura con _track = {}
    state = fields.Selection(
        selection=[('empty', 'Without invoices'),
                   ('invoices', 'With invoices')],
        string='State', readonly=True, default='empty')
    renewal_state = fields.Selection(
        selection=[('not_renewed', 'Agreement not renewed'),
                   ('renewed', 'Agreement renewed')],
        string='Renewal state', readonly=True, default='not_renewed')
    notes = fields.Text('Notes')
    currency_id = fields.Many2one(
        comodel_name='res.currency', string='Currency', required=True,
        default=_get_default_currency_id)

    def _check_dates(self, cr, uid, ids, context=None):
        """Check correct dates. When prolongation is unlimited or renewal,
        end_date is False, so doesn't apply.
        @rtype: boolean
        @return: True if dates are correct or don't apply, False otherwise
        """
        if context is None:
            context = {}
        agreements = self.browse(cr, uid, ids, context=context)
        val = True
        for agreement in agreements:
            if agreement.end_date:
                val = val and agreement.end_date > agreement.start_date
        return val

    _constraints = [
        (_check_dates,
         'Agreement end date must be greater than start date',
         ['start_date', 'end_date']),
    ]

    def create(self, cr, uid, vals, context=None):
        # Set start date if empty
        if (('start_date' in vals and not vals['start_date']) or
                ('start_date' not in vals)):
            vals['start_date'] = fields.Date.today()
        # Set agreement number if empty
        if ('number' in vals and not vals['number']) or ('number' not in vals):
            vals['number'] = self.pool['ir.sequence'].get(
                cr, uid, 'account.agreement.sequence')
        return super(Agreement, self).create(cr, uid, vals, context=context)

    def copy(self, cr, uid, orig_id, default=None, context=None):
        if default is None:
            default = {}
        if context is None:
            context = {}
        context_wo_lang = context.copy()
        agreement_line_obj = self.pool[
            'account.periodical_invoicing.agreement.line']
        if 'lang' in context:
            del context_wo_lang['lang']
        # dont' name the variable agreement
        agreement_record = self.browse(cr, uid, orig_id)
        # Read agreement_lines
        lines = []
        for line in agreement_record.agreement_line:
            data = agreement_line_obj.read(
                cr, uid, line.id, context=context_wo_lang)
            if data:
                del data['last_invoice_date']
                del data['id']
                del data['agreement_id']
                data['product_id'] = data['product_id'][0]
                lines.append(data)
        default.update({
            'state': 'empty',
            'number': False,
            'active': True,
            'name': '%s*' % agreement_record.name,
            'start_date': False,
            'invoice_line': [],
            'renewal_line': [],
            'agreement_line': [(0, 0, x) for x in lines]
        })
        return super(Agreement, self).copy(cr, uid, orig_id, default, context)

    def onchange_start_date(self, cr, uid, ids, start_date=False):
        """It changes last renovation date to the new start date.
        @rtype: dictionary
        @return: field last_renovation_date with new start date
        """
        if not start_date:
            return {}
        result = {'value': {'last_renovation_date': start_date}}
        return result

    def _invoice_created(
            self, cr, uid, agreement, agreement_lines_invoiced, invoice_id,
            context=None):
        """It triggers actions after invoice is created. It can be used for
        e-mail notification. This method can be overriden for extending its
        functionality thanks to its parameters.
        """
        pass

    def _get_next_invoice_date(self, agreement, line, startDate, context=None):
        """Get next date when an invoice has to been generated for an
        agreement line, starting from given date.
        @param line: Agreement line.
        @param startDate: Start date from which next invoice date is
          calculated.
        @rtype: datetime.
        @return: Next invoice date starting from the given date.
        """
        next_date = fields.Date.from_string(agreement.start_date)
        while next_date <= startDate:
            next_date = self._get_next_term_date(
                next_date, line.invoicing_unit, line.invoicing_interval)
        return next_date

    @api.model
    def make_invoices_planned(self):
        """Check if there is any pending invoice to create from each agreement.
        """
        agreements = self.search([])
        today = datetime.date.today()
        grouped_invoices = {}
        for agreement in agreements:
            # check dates
            agreement_start_date = fields.Date.from_string(
                agreement.start_date)
            if (agreement_start_date <= today and
                    (agreement.prolong == 'unlimited' or today <=
                     fields.Date.from_string(agreement.next_expiration_date))):
                # Agreement is still valid
                lines_to_invoice = OrderedDict()
                # Check if there is any agreement line to invoice
                for line in agreement.agreement_line:
                    if not line.active_chk:
                        continue
                    # Check next date of invoicing for this line
                    if line.last_invoice_date:
                        last_invoice_date = fields.Date.from_string(
                            line.last_invoice_date)
                        next_invoice_date = self._get_next_invoice_date(
                            agreement, line, last_invoice_date)
                    else:
                        next_invoice_date = agreement_start_date
                    if next_invoice_date <= today:
                        # Add to a dictionary to invoice all lines together
                        lines_to_invoice[line] = next_invoice_date
                # Invoice all pending lines
                if lines_to_invoice:
                    invoice_id = self.create_invoice(
                        agreement, lines_to_invoice, grouped_invoices)
                    # Call 'event' method
                    self._invoice_created(
                        agreement, lines_to_invoice, invoice_id)

    def _prepare_invoice(self, cr, uid, agreement, context=None):
        invoice_vals = {
            'origin': agreement.number,
            'partner_id': agreement.partner_id.id,
            'type': 'out_invoice',
            'state': 'draft',
            'currency_id': agreement.currency_id.id,
            'company_id': agreement.company_id.id,
            'reference_type': 'none',
            'check_total': 0.0,
            'internal_number': False,
            'user_id': agreement.partner_id.user_id.id,
        }
        # Get other invoice values from agreement partner
        invoice_vals.update(self.pool['account.invoice'].onchange_partner_id(
            cr, uid, [], type=invoice_vals['type'],
            partner_id=agreement.partner_id.id,
            company_id=agreement.company_id.id)['value'], context=context)
        return invoice_vals

    def create_invoice(self, cr, uid, agreement, agreement_lines,
                       grouped_invoices, context=None):
        """Method that creates an invoice from given data.
        @param agreement: Agreement from which invoice is going to be
          generated.
        @param agreement_lines: Dictionary with agreement lines as keys and
          next invoice date of that line as values.
        """
        invoice_obj = self.pool['account.invoice']
        invoice_line_obj = self.pool['account.invoice.line']
        lang_obj = self.pool['res.lang']
        # Get lang record for format purposes
        lang_ids = lang_obj.search(
            cr, uid, [('code', '=', agreement.partner_id.lang)])
        lang = lang_obj.browse(cr, uid, lang_ids)[0]
        ctx = context.copy()
        ctx['lang'] = agreement.partner_id.lang
        ctx['company_id'] = agreement.company_id.id
        ctx['force_company'] = agreement.company_id.id
        ctx['type'] = 'out_invoice'
        invoice_vals = self._prepare_invoice(cr, uid, agreement, context=ctx)
        # Prepare invoice lines objects
        agreement_lines_ids = []
        invoice_lines_vals = []
        for agreement_line in agreement_lines.keys():
            invoice_line = {
                'product_id': agreement_line.product_id.id,
                'quantity': agreement_line.quantity,
                'discount': agreement_line.discount,
                'sequence': agreement_line.sequence,
            }
            # get other invoice line values from agreement line product
            invoice_line.update(invoice_line_obj.product_id_change(
                cr, uid, [], product=agreement_line.product_id.id,
                uom_id=False, qty=agreement_line.quantity,
                partner_id=agreement.partner_id.id,
                fposition_id=invoice_vals['fiscal_position'],
                context=ctx)['value'])
            if agreement_line.price > 0:
                invoice_line['price_unit'] = agreement_line.price
            # Put line taxes
            invoice_line['invoice_line_tax_id'] = \
                [(6, 0, tuple(invoice_line['invoice_line_tax_id']))]
            # Put custom description
            if agreement_line.additional_description:
                invoice_line['name'] += (" " +
                                         agreement_line.additional_description)
            # Put period string
            next_invoice_date = agreement_lines[agreement_line]
            if agreement.period_type == 'pre-paid':
                from_date = next_invoice_date
                to_date = (self._get_next_term_date(
                    next_invoice_date, agreement_line.invoicing_unit,
                    agreement_line.invoicing_interval) - timedelta(days=1))
            else:
                from_date = self._get_previous_term_date(
                    next_invoice_date, agreement_line.invoicing_unit,
                    agreement_line.invoicing_interval)
                to_date = next_invoice_date - timedelta(days=1)

            def _get_period_text(cr, uid, context=None):
                """Method for getting the text in the partner language"""
                return _('Period: from %s to %s')

            invoice_line['name'] += (
                "\n" + _get_period_text(cr, uid, context=ctx) % (
                    from_date.strftime(lang.date_format),
                    to_date.strftime(lang.date_format)))
            invoice_lines_vals.append(invoice_line)
            agreement_lines_ids.append(agreement_line.id)
        key = (agreement.partner_id.id, agreement.currency_id.id)
        if (agreement.partner_id.group_agreement_invoices and
                grouped_invoices.get(key)):
            invoice_id = grouped_invoices[key]
            # add lines to the existing invoice
            for invoice_line_vals in invoice_lines_vals:
                invoice_line_vals['invoice_id'] = invoice_id
                invoice_line_obj.create(
                    cr, uid, invoice_line_vals, context=ctx)
                # Update origin field
                invoice = invoice_obj.browse(cr, uid, invoice_id)
                invoice_obj.write(
                    cr, uid, invoice_id,
                    {'origin': invoice.origin + ";" + agreement.number})
        else:
            # Add lines to the invoice dictionary
            invoice_vals['invoice_line'] = [(0, 0, x) for x in
                                            invoice_lines_vals]
            invoice_id = invoice_obj.create(cr, uid, invoice_vals, context=ctx)
            grouped_invoices[key] = invoice_id
        invoice_obj.button_reset_taxes(cr, uid, invoice_id, context=context)
        # Update last invoice date for lines
        self.pool['account.periodical_invoicing.agreement.line'].write(
            cr, uid, agreement_lines_ids,
            {'last_invoice_date': fields.Date.today()}, context=ctx)
        # Create invoice agreement record
        agreement_invoice = {
            'agreement_id': agreement.id,
            'date': fields.Date.today(),
            'invoice_id': invoice_id,
        }
        self.pool['account.periodical_invoicing.agreement.invoice'].create(
            cr, uid, agreement_invoice, context=ctx)
        # Update agreement state
        if agreement.state != 'invoices':
            self.pool['account.periodical_invoicing.agreement'].write(
                cr, uid, [agreement.id], {'state': 'invoices'},
                context=ctx)
        return invoice_id


class AgreementLine(models.Model):
    _name = 'account.periodical_invoicing.agreement.line'
    _order = 'sequence, id'

    sequence = fields.Integer(default=10)
    active_chk = fields.Boolean(
        string='Active', default=True,
        help='Unchecking this field, this quota is not generated')
    agreement_id = fields.Many2one(
        'account.periodical_invoicing.agreement', 'Agreement reference',
        ondelete='cascade')
    product_id = fields.Many2one(
        'product.product', 'Product', ondelete='set null', required=True)
    name = fields.Char(
        related='product_id.name', string='Description', store=False)
    additional_description = fields.Text(
        string='Add. description',
        help='Additional description that will be added to the product '
             'description on invoices.')
    quantity = fields.Float(
        string='Quantity', required=True, default=1,
        help='Quantity of the product to invoice')
    price = fields.Float(
        'Product price', digits_compute=dp.get_precision('Account'),
        help='Specific price for this product. Keep empty to use the '
             'current price while generating invoice')
    discount = fields.Float('Discount (%)', digits=(16, 2))
    invoicing_interval = fields.Integer(
        string='Interval', required=True, default=1,
        help="Interval in time units for invoicing this product")
    invoicing_unit = fields.Selection(
        selection=[('days', 'days'),
                   ('weeks', 'weeks'),
                   ('months', 'months'),
                   ('years', 'years')],
        string='Interval unit', required=True, default='months')
    last_invoice_date = fields.Date(string='Last invoice')

    _sql_constraints = [
        ('line_qty_zero', 'CHECK (quantity > 0)',
         'All product quantities must be greater than 0.\n'),
        ('line_interval_zero', 'CHECK (invoicing_interval > 0)',
         'All invoicing intervals must be greater than 0.\n'),
    ]

    def copy(self, cr, uid, orig_id, default=None, context=None):
        if default is None:
            default = {}
        default.update({
            'last_invoice_date': False,
        })
        return super(AgreementLine, self).copy(cr, uid, orig_id, default,
                                               context=context)

    def onchange_product_id(self, cr, uid, ids, product_id=False,
                            context=None):
        result = {}
        if product_id:
            product = self.pool['product.product'].browse(
                cr, uid, product_id, context=context)
            if product:
                result['value'] = {'name': product['name']}
        return result


class AgreementInvoice(models.Model):
    """Class for recording each invoice created for each line of the agreement.
    It keeps only reference to the agreement, not to the line.
    """
    _name = 'account.periodical_invoicing.agreement.invoice'

    agreement_id = fields.Many2one(
        'account.periodical_invoicing.agreement', 'Agreement reference',
        ondelete='cascade')
    date = fields.Datetime(
        related='invoice_id.create_date', string="Date of invoice creation",
        store=False)
    invoice_id = fields.Many2one(
        comodel_name='account.invoice', string='Invoice', ondelete='cascade')

    def view_invoice(self, cr, uid, ids, context=None):
        """
        Method for viewing invoice associated to an agreement
        """
        agreement_invoice = \
            self.pool['account.periodical_invoicing.agreement.invoice'].browse(
                cr, uid, ids[0], context=context)
        invoice_id = agreement_invoice.invoice_id.id
        # Get view to show
        data_obj = self.pool['ir.model.data']
        result = data_obj._get_id(cr, uid, 'account', 'invoice_form')
        view_id = data_obj.browse(cr, uid, result).res_id
        # Return view with invoice created
        return {
            'domain': "[('id','=', " + str(invoice_id) + ")]",
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.invoice',
            'context': context,
            'res_id': invoice_id,
            'view_id': [view_id],
            'type': 'ir.actions.act_window',
            'nodestroy': True
        }


class AgreementRenewal(models.Model):
    _name = 'account.periodical_invoicing.agreement.renewal'

    agreement_id = fields.Many2one(
        'account.periodical_invoicing.agreement', 'Agreement reference',
        ondelete='cascade', index=True)
    date = fields.Date('Date', help="Date of the renewal")
    comments = fields.Char('Comments', size=200, help='Renewal comments')

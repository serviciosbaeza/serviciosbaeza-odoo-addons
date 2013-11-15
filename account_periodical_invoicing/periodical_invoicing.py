# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2012 Serv. Tecnol. Avanzados (http://www.serviciosbaeza.com) All Rights Reserved.
#                       Pedro M. Baeza <pedro.baeza@serviciosbaeza.com> 
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
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
from openerp.osv import orm, fields
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT 
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import openerp.addons.decimal_precision as dp

class agreement(orm.Model):
    _name = 'account.periodical_invoicing.agreement'
    _inherit = 'mail.thread'
    _description = "Periodical invoicing agreement"

    def __get_next_term_date(self, date, unit, interval):
        """
        Get the date that results on incrementing given date an interval of time in time unit.
        @param date: Original date.
        @param unit: Interval time unit.
        @param interval: Quantity of the time unit.
        @rtype: date
        @return: The date incremented in 'interval' units of 'unit'.    
        """
        if unit == 'days':
            return date + timedelta(days = interval)
        elif unit == 'weeks':
            return date + timedelta(weeks=interval)
        elif unit == 'months':
            return date + relativedelta(months=interval)
        elif unit == 'years':
            return date + relativedelta(years=interval)
        
    def __get_previous_term_date(self, date, unit, interval):
        """
        Get the date that results on decrementing given date an interval of time in time unit.
        @param date: Original date.
        @param unit: Interval time unit.
        @param interval: Quantity of the time unit.
        @rtype: date
        @return: The date decremented in 'interval' units of 'unit'.    
        """
        if unit == 'days':
            return date - timedelta(days = interval)
        elif unit == 'weeks':
            return date - timedelta(weeks=interval)
        elif unit == 'months':
            return date - relativedelta(months=interval)
        elif unit == 'years':
            return date - relativedelta(years=interval)
        
    def __get_next_expiration_date(self, cr, uid, ids, field_name, arg, context=None):
        """
        Get next expiration date of the agreement. For unlimited agreements, get max date 
        """
        if not ids: return {}
        res = {}
        for agreement in self.browse(cr, uid, ids):
            if agreement.prolong == 'fixed':
                res[agreement.id] = agreement.end_date
            elif agreement.prolong == 'unlimited':
                now = datetime.now()
                date = self.__get_next_term_date(datetime.strptime(agreement.start_date, "%Y-%m-%d"), agreement.prolong_unit, agreement.prolong_interval)
                while (date < now):
                    date = self.__get_next_term_date(date, agreement.prolong_unit, agreement.prolong_interval)
                res[agreement.id] = date
            else:
                # for renewable fixed term
                res[agreement.id] = self.__get_next_term_date(datetime.strptime( \
                    agreement.last_renovation_date if agreement.last_renovation_date else agreement.start_date, "%Y-%m-%d"), \
                    agreement.prolong_unit, agreement.prolong_interval)
        return res

    _columns = {
        'name': fields.char('Name', size=100, select=1, required=True, help='Name that helps to identify the agreement'),
        'number': fields.char('Agreement number', select=1, size=32, help="Number of agreement. Keep empty to get the number assigned by a sequence."),
        'active': fields.boolean('Active', help='Unchecking this field, quotas are not generated'),
        'partner_id': fields.many2one('res.partner', 'Customer', select=1, change_default=True, required=True, help="Customer you are making the agreement with"),
        'company_id': fields.many2one('res.company', 'Company', required=True, help="Company that signs the agreement"),
        'start_date': fields.date('Start date', select=1, help="Beginning of the agreement. Keep empty to use the current date"),
        'prolong': fields.selection([('recurrent','Renewable fixed term'),('unlimited','Unlimited term'),('fixed','Fixed term')], 'Prolongation', help="Sets the term of the agreement. 'Renewable fixed term': It sets a fixed term, but with possibility of manual renew; 'Unlimited term': Renew is made automatically; 'Fixed term': The term is fixed and there is no possibility to renew."),
        'end_date': fields.date('End date', help="End date of the agreement"),
        'prolong_interval': fields.integer('Interval', help="Interval in time units to prolong the agreement until new renewall (that is automatic for unlimited term, manual for renewable fixed term)."),
        'prolong_unit': fields.selection([('days','days'),('weeks','weeks'),('months','months'),('years','years')], 'Interval unit', help='Time unit for the prolongation interval'),
        'agreement_line': fields.one2many('account.periodical_invoicing.agreement.line', 'agreement_id', 'Agreement lines'),
        'invoice_line': fields.one2many('account.periodical_invoicing.agreement.invoice', 'agreement_id', 'Invoice lines', readonly=True),
        'renewal_line': fields.one2many('account.periodical_invoicing.agreement.renewal', 'agreement_id', 'Renewal lines', readonly=True),
        'last_renovation_date': fields.date('Last renovation date', help="Last date when agreement was renewed (same as start date if not renewed)"),
        'next_expiration_date': fields.function(__get_next_expiration_date, string='Next expiration date', type='date', method=True, store=True),
        'period_type': fields.selection([('pre-paid', 'Pre-paid'), ('post-paid', 'Post-paid')], "Period type", required=True, help="Period type for invoicing. 'Pre-paid': Invoices are generated for the upcoming period. 'Post-paid': Invoices are generated for the consumed period."),
        #TODO: Añadir posibilidad de seguir cuando se genera una factura con _track = {}
        'state': fields.selection([('empty', 'Without invoices'), ('invoices', 'With invoices')], 'State', readonly=True),
        'renewal_state': fields.selection([('not_renewed', 'Agreement not renewed'), ('renewed', 'Agreement renewed')], 'Renewal state', readonly=True),
        'notes': fields.text('Notes'),
    }

    _defaults = {
        'active': lambda *a: 1,
        'company_id': lambda s, cr, uid, c: s.pool.get('res.company')._company_default_get(cr, uid, 'account', context=c),
        'period_type': lambda *a: 'pre-paid',
        'prolong': lambda *a: 'unlimited',
        'prolong_interval': lambda *a: 1,
        'prolong_unit': lambda *a: 'years',
        'state': lambda *a: 'empty',
        'renewal_state': lambda *a: 'not_renewed',
    }
    
    def _check_dates(self, cr, uid, ids, context=None):
        """
        Check correct dates. When prolongation is unlimited or renewal, end_date is False, so doesn't apply
        @rtype: boolean
        @return: True if dates are correct or don't apply, False otherwise
        """
        if context == None: context = {}
        agreements = self.browse(cr, uid, ids, context=context)
        val = True
        for agreement in agreements:
            if agreement.end_date: val = val and agreement.end_date > agreement.start_date
        return val

    _constraints = [
        (_check_dates, 'Agreement end date must be greater than start date', ['start_date','end_date']),
    ]
        
    def create(self, cr, uid, vals, context=None):
        # Set start date if empty
        if ('start_date' in vals and not vals['start_date']) or ('start_date' not in vals):
            vals['start_date'] = datetime.now()
        # Set agreement number if empty
        if ('number' in vals and not vals['number']) or ('number' not in vals):
            vals['number'] = self.pool.get('ir.sequence').get(cr, uid, 'account.agreement.sequence')
        return super(agreement, self).create(cr, uid, vals, context=context)
    
    def copy(self, cr, uid, orig_id, default={}, context=None):
        if default is None:
            default = {}
        if context is None:
            context = {}
        context_wo_lang = context.copy()
        agreement_line_obj = self.pool.get('account.periodical_invoicing.agreement.line')
        if 'lang' in context:
            del context_wo_lang['lang']
        agreement_record = self.browse(cr, uid, orig_id) # dont' name the variable agreement
        # Read agreement_lines
        lines = []
        for line in agreement_record.agreement_line:
            data = agreement_line_obj.read(cr, uid, line.id, context=context_wo_lang)
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
        return super(agreement, self).copy(cr, uid, orig_id, default, context)

    def onchange_start_date(self, cr, uid, ids, start_date=False):
        """
        It changes last renovation date to the new start date.
        @rtype: dictionary
        @return: field last_renovation_date with new start date
        """
        if not start_date: return {}
        result = {}
        result['value'] = { 'last_renovation_date': start_date }
        return result

    def _invoice_created(self, cr, uid, agreement, agreement_lines_invoiced, invoice_id, context={}):
        """
        It triggers actions after invoice is created. It can be used for e-mail notification.
        This method can be overriden for extending its functionality thanks to its parameters.
        """
        pass

    def _get_next_invoice_date(self, agreement, line, startDate, context={}):
        """
        Get next date when an invoice has to been generated for an agreement line, starting from given date.
        @param line: Agreement line.
        @param startDate: Start date from which next invoice date is calculated.
        @rtype: datetime.
        @return: Next invoice date starting from the given date.  
        """
        next_date = datetime.strptime(agreement.start_date, '%Y-%m-%d')
        while next_date <= startDate:
            next_date = self.__get_next_term_date(next_date, line.invoicing_unit, line.invoicing_interval)
        return next_date

    def make_invoices_planned(self, cr, uid, context={}):
        """
        Check if there is any pending invoice to create from each agreement. 
        """
        if context is None:
            context = {}
        ids = self.search(cr, uid, [])
        now = datetime.now()
        for agreement in self.browse(cr, uid, ids, context=context):
            if not agreement.active: continue
            # check dates
            agreement_start_date = datetime.strptime(agreement.start_date, 
                                                    DEFAULT_SERVER_DATE_FORMAT)
            if (agreement_start_date < now and 
                    (agreement.prolong == 'unlimited' 
                     or now <= datetime.strptime(
                     agreement.next_expiration_date, 
                     DEFAULT_SERVER_DATE_FORMAT)
                    )):
                # Agreement is still valid
                lines_to_invoice = {}
                # Check if there is any agreement line to invoice 
                for line in agreement.agreement_line:
                    if line.active_chk:
                        # Check next date of invoicing for this line
                        if line.last_invoice_date:
                            last_invoice_date = datetime.strptime(
                                line.last_invoice_date, 
                                DEFAULT_SERVER_DATE_FORMAT)
                            next_invoice_date = self._get_next_invoice_date(
                                agreement, line, last_invoice_date)
                        else:
                            next_invoice_date = agreement_start_date
                        if next_invoice_date <= now:
                            # Add to a dictionary to invoice all lines together
                            lines_to_invoice[line] = next_invoice_date
                # Invoice all pending lines
                if len(lines_to_invoice) > 0:
                    invoice_id = self.create_invoice(cr, uid, agreement, lines_to_invoice, context=context)
                    # Call 'event' method
                    self._invoice_created(cr, uid, agreement, lines_to_invoice, invoice_id, context=context)

    def create_invoice(self, cr, uid, agreement, agreement_lines, context={}):
        """
        Method that creates an invoice from given data.
        @param agreement: Agreement from which invoice is going to be generated.  
        @param agreement_lines: Dictionary with agreement lines as keys and next invoice date of that line as values. 
        """
        now = datetime.now()
        invoice_obj = self.pool.get('account.invoice')
        invoice_line_obj = self.pool.get('account.invoice.line')
        lang_obj = self.pool.get('res.lang')
        # Get lang record for format purposes
        lang_ids = lang_obj.search(cr, uid, [('code', '=', agreement.partner_id.lang)])
        lang = lang_obj.browse(cr, uid, lang_ids)[0]
        # Create invoice object
        context['company_id'] = agreement.company_id.id
        context['force_company'] = agreement.company_id.id
        context['type'] = 'out_invoice'
        invoice = {
            'date_invoice': now.strftime('%Y-%m-%d'),
            'origin': agreement.number,
            'partner_id': agreement.partner_id.id,
            'journal_id': invoice_obj._get_journal(cr, uid, context),
            'type': 'out_invoice',
            'state': 'draft',
            'currency_id': invoice_obj._get_currency(cr, uid, context),
            'company_id': agreement.company_id.id,
            'reference_type': 'none',
            'check_total': 0.0,
            'internal_number': False,
            'user_id': agreement.partner_id.user_id.id,
        }
        # Get other invoice values from agreement partner
        invoice.update(invoice_obj.onchange_partner_id(cr, uid, [], type=invoice['type'], partner_id=agreement.partner_id.id, company_id=agreement.company_id.id)['value'])
        # Prepare invoice lines objects
        agreement_lines_ids = []
        invoice_lines = []
        for agreement_line in agreement_lines.keys():
            invoice_line = {
                'product_id': agreement_line.product_id.id,
                'quantity': agreement_line.quantity,
                'discount': agreement_line.discount,
            }
            # get other invoice line values from agreement line product
            invoice_line.update(invoice_line_obj.product_id_change(cr, uid, [],
                    product=agreement_line.product_id.id, uom_id=False,
                    qty=agreement_line.quantity,
                    partner_id=agreement.partner_id.id,
                    fposition_id=invoice['fiscal_position'],
                    context=context)['value'])
            # Put line taxes
            invoice_line['invoice_line_tax_id'] = [(6, 0, tuple(invoice_line['invoice_line_tax_id']))]
            # Put custom description
            if agreement_line.additional_description:
                invoice_line['name'] += " " + agreement_line.additional_description
            # Put period string
            next_invoice_date = agreement_lines[agreement_line]
            if agreement.period_type == 'pre-paid':
                from_date = next_invoice_date
                to_date = (self.__get_next_term_date(next_invoice_date,
                                        agreement_line.invoicing_unit,
                                        agreement_line.invoicing_interval) -
                                        timedelta(days=1))
            else:
                from_date = self.__get_previous_term_date(next_invoice_date,
                                            agreement_line.invoicing_unit,
                                            agreement_line.invoicing_interval)
                to_date = next_invoice_date - timedelta(days=1)
            invoice_line['name'] += "\n" + _('Period: from %s to %s') %(
                                        from_date.strftime(lang.date_format),
                                        to_date.strftime(lang.date_format))
            invoice_lines.append(invoice_line)
            agreement_lines_ids.append(agreement_line.id)
        # Add lines to invoice and create it
        invoice['invoice_line'] = [(0, 0, x) for x in invoice_lines]
        invoice_id = invoice_obj.create(cr, uid, invoice, context=context)
        # Update last invoice date for lines
        self.pool.get('account.periodical_invoicing.agreement.line').write(cr, uid, agreement_lines_ids, {'last_invoice_date': now.strftime('%Y-%m-%d')} ,context=context)
        # Update agreement state
        if agreement.state != 'invoices':
            self.pool.get('account.periodical_invoicing.agreement').write(cr, uid, [agreement.id], {'state': 'invoices'} ,context=context)
        # Create invoice agreement record
        agreement_invoice = {
            'agreement_id': agreement.id,
            'date': now.strftime('%Y-%m-%d'),
            'invoice_id': invoice_id
        }
        self.pool.get('account.periodical_invoicing.agreement.invoice').create(cr, uid, agreement_invoice, context=context)
        return invoice_id


class agreement_line(orm.Model):

    _name = 'account.periodical_invoicing.agreement.line'
    _columns = {
        'active_chk': fields.boolean('Active', help='Unchecking this field, this quota is not generated'),
        'agreement_id': fields.many2one('account.periodical_invoicing.agreement', 'Agreement reference', ondelete='cascade'),
        'product_id': fields.many2one('product.product', 'Product', ondelete='set null', required=True),
        'name': fields.related('product_id', 'name', type="char", relation='product.product', string='Description', store=False),
        'additional_description': fields.char('Add. description', size=30, help='Additional description that will be added to the product description on invoices.'),
        'quantity': fields.float('Quantity', required=True, help='Quantity of the product to invoice'),
        'discount': fields.float('Discount (%)', digits=(16, 2)),
        'invoicing_interval': fields.integer('Interval', help="Interval in time units for invoicing this product", required=True),
        'invoicing_unit': fields.selection([('days','days'),('weeks','weeks'),('months','months'),('years','years')], 'Interval unit', required=True),
        'last_invoice_date': fields.date('Last invoice'),
    }

    _defaults = {
        'active_chk': lambda *a: 1,
        'quantity': lambda *a: 1,
        'invoicing_interval': lambda *a: 1,
        'invoicing_unit': lambda *a: 'months',
    }
    
    _sql_constraints = [
        ('line_qty_zero', 'CHECK (quantity > 0)',  'All product quantities must be greater than 0.\n'),
        ('line_interval_zero', 'CHECK (invoicing_interval > 0)',  'All invoicing intervals must be greater than 0.\n'),
    ]

    def copy(self, cr, uid, orig_id, default=None, context=None):
        if default is None: default = {}
        default.update({
            'last_invoice_date': False,
        })
        return super(agreement_line, self).copy(cr, uid, orig_id, default, context)

    def onchange_product_id(self, cr, uid, ids, product_id=False, context={}):
        result = {}
        if product_id:
            product = self.pool.get('product.product').browse(cr, uid, product_id, context=context)
            if product:
                result['value'] = { 'name': product['name'] }
        return result


class agreement_invoice(orm.Model):
    """
    Class for recording each invoice created for each line of the agreement. It keeps only reference to the agreement, not to the line.
    """
    _name = 'account.periodical_invoicing.agreement.invoice'
    _columns = {
        'agreement_id': fields.many2one('account.periodical_invoicing.agreement', 'Agreement reference', ondelete='cascade'),
        'date': fields.related('invoice_id', 'date_invoice', type='date', relation='account.invoice', string="Date of invoice creation", store=False),
        'invoice_id': fields.many2one('account.invoice', 'Invoice', ondelete='cascade'),
    }

    def view_invoice(self, cr, uid, ids, context={}):
        """
        Method for viewing invoice associated to an agreement
        """
        agreement_invoice = self.pool.get('account.periodical_invoicing.agreement.invoice').browse(cr, uid, ids[0], context=context)
        invoice_id = agreement_invoice.invoice_id.id
        # Get view to show
        data_obj = self.pool.get('ir.model.data')
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


class agreement_renewal(orm.Model):
    _name = 'account.periodical_invoicing.agreement.renewal'
    _columns = {
        'agreement_id': fields.many2one('account.periodical_invoicing.agreement', 'Agreement reference', ondelete='cascade', select=True),
        'date': fields.date('Date', help="Date of the renewal"),
        'comments': fields.char('Comments', size=200, help='Renewal comments'),
    }

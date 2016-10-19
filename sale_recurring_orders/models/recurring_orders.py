# -*- coding: utf-8 -*-
# (c) 2015 Serv. Tecnol. Avanzados - Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, fields, api, exceptions, _
from datetime import timedelta
from dateutil.relativedelta import relativedelta
import openerp.addons.decimal_precision as dp


class Agreement(models.Model):
    _name = 'sale.recurring_orders.agreement'
    _inherit = ['mail.thread']
    _description = "Recurring orders agreement"

    @api.model
    def __get_next_term_date(self, date, unit, interval):
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

    @api.multi
    def _compute_next_expiration_date(self):
        for agreement in self:
            if agreement.prolong == 'fixed':
                agreement.next_expiration_date = agreement.end_date
            elif agreement.prolong == 'unlimited':
                now = fields.Date.from_string(fields.Date.today())
                date = self.__get_next_term_date(
                    fields.Date.from_string(agreement.start_date),
                    agreement.prolong_unit, agreement.prolong_interval)
                while date < now:
                    date = self.__get_next_term_date(
                        date, agreement.prolong_unit,
                        agreement.prolong_interval)
                agreement.next_expiration_date = date
            else:
                # for renewable fixed term
                agreement.next_expiration_date = self.__get_next_term_date(
                    fields.Date.from_string(agreement.last_renovation_date or
                                            agreement.start_date),
                    agreement.prolong_unit, agreement.prolong_interval)

    def _default_company_id(self):
        company_model = self.env['res.company']
        company_id = company_model._company_default_get('sale')
        return company_model.browse(company_id)

    name = fields.Char(
        string='Name', size=100, index=True, required=True,
        help='Name that helps to identify the agreement')
    number = fields.Char(
        string='Agreement number', index=True, size=32, copy=False,
        help="Number of agreement. Keep empty to get the number assigned by a "
             "sequence.")
    active = fields.Boolean(
        string='Active', default=True,
        help='Unchecking this field, quotas are not generated')
    partner_id = fields.Many2one(
        comodel_name='res.partner', string='Customer', index=True,
        change_default=True, required=True,
        help="Customer you are making the agreement with")
    company_id = fields.Many2one(
        comodel_name='res.company', string='Company', required=True,
        help="Company that signs the agreement", default=_default_company_id)
    start_date = fields.Date(
        string='Start date', index=True, copy=False,
        help="Beginning of the agreement. Keep empty to use the current date")
    prolong = fields.Selection(
        selection=[('recurrent', 'Renewable fixed term'),
                   ('unlimited', 'Unlimited term'),
                   ('fixed', 'Fixed term')],
        string='Prolongation', default='unlimited',
        help="Sets the term of the agreement. 'Renewable fixed term': It sets "
             "a fixed term, but with possibility of manual renew; 'Unlimited "
             "term': Renew is made automatically; 'Fixed term': The term is "
             "fixed and there is no possibility to renew.", required=True)
    end_date = fields.Date(
        string='End date', help="End date of the agreement")
    prolong_interval = fields.Integer(
        string='Interval', default=1,
        help="Interval in time units to prolong the agreement until new "
             "renewable (that is automatic for unlimited term, manual for "
             "renewable fixed term).")
    prolong_unit = fields.Selection(
        selection=[('days', 'days'),
                   ('weeks', 'weeks'),
                   ('months', 'months'),
                   ('years', 'years')],
        string='Interval unit', default='years',
        help='Time unit for the prolongation interval')
    agreement_line = fields.One2many(
        comodel_name='sale.recurring_orders.agreement.line',
        inverse_name='agreement_id', string='Agreement lines')
    order_line = fields.One2many(
        comodel_name='sale.order', copy=False, inverse_name='agreement_id',
        string='Orders', readonly=True)
    renewal_line = fields.One2many(
        comodel_name='sale.recurring_orders.agreement.renewal', copy=False,
        inverse_name='agreement_id', string='Renewal lines', readonly=True)
    last_renovation_date = fields.Date(
        string='Last renovation date',
        help="Last date when agreement was renewed (same as start date if not "
             "renewed)")
    next_expiration_date = fields.Date(
        compute="_compute_next_expiration_date", string='Next expiration date')
    # TODO: Añadir posibilidad de track al generar una factura
    state = fields.Selection(
        selection=[('empty', 'Without orders'),
                   ('first', 'First order created'),
                   ('orders', 'With orders')],
        string='State', readonly=True, default='empty')
    renewal_state = fields.Selection(
        selection=[('not_renewed', 'Agreement not renewed'),
                   ('renewed', 'Agreement renewed')],
        string='Renewal state', readonly=True, default='not_renewed')
    notes = fields.Text('Notes')

    _sql_constraints = [
        ('number_uniq', 'unique(number)', 'Agreement number must be unique !'),
    ]

    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        """Check correct dates. When prolongation is unlimited or renewal,
        end_date is False, so doesn't apply
        """
        for record in self:
            if record.end_date and record.end_date < record.start_date:
                raise exceptions.Warning(
                    _('Agreement end date must be greater than start date'))

    @api.model
    def create(self, vals):
        # Set start date if empty
        if not vals.get('start_date'):
            vals['start_date'] = fields.Date.today()
        # Set agreement number if empty
        if not vals.get('number'):
            vals['number'] = self.env['ir.sequence'].get(
                'sale.r_o.agreement.sequence')
        return super(Agreement, self).create(vals)

    @api.multi
    def write(self, vals):
        value = super(Agreement, self).write(vals)
        if (any(vals.get(x) is not None for x in
                ['active', 'number', 'agreement_line', 'prolong', 'end_date',
                 'prolong_interval', 'prolong_unit', 'partner_id'])):
            # unlink all future orders
            self.unlink_orders(fields.Date.today())
        return value

    @api.model
    def copy(self, id, default=None):
        agreement_record = self.browse(id)
        default.update({
            'state': 'empty',
            'active': True,
            'name': '%s*' % agreement_record['name'],
        })
        return super(Agreement, self).copy(id, default=default)

    @api.multi
    def unlink(self):
        for agreement in self:
            if any(agreement.mapped('order_line')):
                raise exceptions.Warning(
                    _('You cannot remove agreements with confirmed orders!'))
        self.unlink_orders(fields.Date.from_string(fields.Date.today()))
        return models.Model.unlink(self)

    @api.multi
    def onchange_start_date(self, start_date=False):
        """It changes last renovation date to the new start date.
        @rtype: dictionary
        @return: field last_renovation_date with new start date
        """
        if not start_date:
            return {}
        result = {'value': {'last_renovation_date': start_date}}
        return result

    @api.model
    def revise_agreements_expirations_planned(self):
        """Check each active unlimited agreement to see if the end is near."""
        for agreement in self.search([('prolong', '=', 'unlimited')]):
            if agreement.next_expiration_date <= fields.Date.today():
                # force recalculate next_expiration_date
                agreement.write({'prolong': 'unlimited'})
        return True

    @api.model
    def _prepare_sale_order_vals(self, agreement, date):
        order_obj = self.env['sale.order'].with_context(
            company_id=agreement.company_id.id)
        order_vals = {
            'date_order': date,
            'date_confirm': date,
            'origin': agreement.number,
            'partner_id': agreement.partner_id.id,
            'state': 'draft',
            'company_id': agreement.company_id.id,
            'from_agreement': True,
            'agreement_id': agreement.id,
        }
        # Get other order values from agreement partner
        order_vals.update(order_obj.onchange_partner_id(
            agreement.partner_id.id)['value'])
        order_vals['user_id'] = agreement.partner_id.user_id.id
        return order_vals

    @api.model
    def _prepare_sale_order_line_vals(self, agreement_line, order):
        order_line_obj = self.env['sale.order.line'].with_context(
            company_id=self.company_id.id)
        order_line_vals = {
            'order_id': order.id,
            'product_id': agreement_line.product_id.id,
            'product_uom_qty': agreement_line.quantity,
            'discount': agreement_line.discount,
        }
        # get other order line values from agreement line product
        order_line_vals.update(order_line_obj.product_id_change(
            order.pricelist_id.id, product=agreement_line.product_id.id,
            qty=agreement_line.quantity,
            partner_id=order.partner_id.id,
            fiscal_position=order.fiscal_position.id)['value'])
        if agreement_line.specific_price:
            order_line_vals['price_unit'] = agreement_line.specific_price
        # Put line taxes
        order_line_vals['tax_id'] = [(6, 0, tuple(order_line_vals['tax_id']))]
        # Put custom description
        if agreement_line.additional_description:
            order_line_vals['name'] += " %s" % (
                agreement_line.additional_description)
        return order_line_vals

    @api.multi
    def create_order(self, date, agreement_lines):
        """Method that creates an order from given data.
        @param agreement: Agreement method get data from.
        @param date: Date of created order.
        @param agreement_lines: Lines that will generate order lines.
        """
        self.ensure_one()
        order_line_obj = self.env['sale.order.line'].with_context(
            company_id=self.company_id.id)
        order_vals = self._prepare_sale_order_vals(self, date)
        order = self.env['sale.order'].create(order_vals)
        # Create order lines objects
        for agreement_line in agreement_lines:
            order_line_vals = self._prepare_sale_order_line_vals(
                agreement_line, order)
            order_line_obj.create(order_line_vals)
        # Update last order date for lines
        agreement_lines.write({'last_order_date': fields.Date.today()})
        # Update agreement state
        if self.state != 'orders':
            self.state = 'orders'
        return order

    @api.multi
    def _get_next_order_date(self, line, start_date):
        """Get next date starting from given date when an order is generated.
        @param line: Agreement line
        @param start_date: Start date from which next order date is calculated.
        @rtype: datetime
        @return: Next order date starting from the given date.
        """
        self.ensure_one()
        next_date = fields.Date.from_string(self.start_date)
        while next_date <= start_date:
            next_date = self.__get_next_term_date(
                next_date, line.ordering_unit, line.ordering_interval)
        return next_date

    @api.multi
    def generate_agreement_orders(self, start_date, end_date):
        """Check if there is any pending order to create for given agreement.
        """
        self.ensure_one()
        if not self.active:
            return
        lines_to_order = {}
        exp_date = fields.Date.from_string(self.next_expiration_date)
        if exp_date < end_date and self.prolong != 'unlimited':
            end_date = exp_date
        for line in self.agreement_line:
            # Check if there is any agreement line to order
            if not line.active_chk:
                continue
            # Check future orders for this line until end_date
            next_order_date = self._get_next_order_date(line, start_date)
            while next_order_date <= end_date:
                # Add to a list to order all lines together
                if not lines_to_order.get(next_order_date):
                    lines_to_order[next_order_date] = self.env[
                        'sale.recurring_orders.agreement.line']
                lines_to_order[next_order_date] |= line
                next_order_date = self._get_next_order_date(
                    line, next_order_date)
        # Order all pending lines
        dates = lines_to_order.keys()
        dates.sort()
        for date in dates:
            # Check if an order exists for that date
            order = self.order_line.filtered(
                lambda x: (
                    fields.Date.to_string(
                        fields.Datetime.from_string(x.date_order)) ==
                    fields.Date.to_string(date)))
            if not order:
                # create it if not exists
                self.create_order(
                    fields.Date.to_string(date), lines_to_order[date])

    @api.multi
    def generate_initial_order(self):
        """Method that creates an initial order with all the agreement lines
        """
        self.ensure_one()
        # Add only active lines
        agreement_lines = self.mapped('agreement_line').filtered('active_chk')
        order = self.create_order(self.start_date, agreement_lines)
        self.write({'state': 'first'})
        order.signal_workflow('order_confirm')
        # Return view with order created
        return {
            'domain': "[('id', '=', %s)]" % order.id,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'sale.order',
            'context': self.env.context,
            'res_id': order.id,
            'view_id': [self.env.ref('sale.view_order_form').id],
            'type': 'ir.actions.act_window',
            'nodestroy': True
        }

    @api.model
    def generate_next_orders_planned(self, years=1, start_date=None):
        """Launch the order generation of active agreements."""
        if start_date:
            start_date = fields.Date.from_string(start_date)
        self.search([]).generate_next_orders(
            years=years, start_date=start_date)

    @api.multi
    def generate_next_year_orders(self):
        return self.generate_next_orders(years=1)

    @api.multi
    def generate_next_orders(self, years=1, start_date=None):
        """Method that generates all the orders of the given agreements for
        the next year, counting from current date.
        """
        if not start_date:
            start_date = fields.Date.from_string(fields.Date.today())
        end_date = start_date + relativedelta(years=years)
        for agreement in self:
            agreement.generate_agreement_orders(start_date, end_date)
        return True

    @api.model
    def confirm_current_orders_planned(self):
        tomorrow = fields.Date.to_string(
            fields.Date.from_string(fields.Date.today()) + timedelta(days=1))
        orders = self.env['sale.order'].search([
            ('aggrement_id', '!=', False),
            ('state', 'in', ('draft', 'sent')),
            ('date_order', '<', tomorrow)
        ])
        for order in orders:
            order.signal_workflow('order_confirm')

    @api.multi
    def unlink_orders(self, start_date):
        """Remove generated orders from given date."""
        orders = self.mapped('order_line').filtered(
            lambda x: (x.state in ('draft', 'sent') and
                       x.date_order >= start_date))
        orders.unlink()


class AgreementLine(models.Model):
    _name = 'sale.recurring_orders.agreement.line'

    active_chk = fields.Boolean(
        string='Active', default=True,
        help='Unchecking this field, this quota is not generated')
    agreement_id = fields.Many2one(
        comodel_name='sale.recurring_orders.agreement',
        string='Agreement reference', ondelete='cascade')
    product_id = fields.Many2one(
        comodel_name='product.product', string='Product', ondelete='set null',
        required=True)
    name = fields.Char(
        related="product_id.name", string='Description', store=False)
    additional_description = fields.Char(
        string='Add. description', size=30,
        help='Additional description that will be added to the product '
             'description on orders.')
    quantity = fields.Float(
        string='Quantity', required=True, help='Quantity of the product',
        default=1.0)
    discount = fields.Float(string='Discount (%)', digits=(16, 2))
    ordering_interval = fields.Integer(
        string='Interval', required=True, default=1,
        help="Interval in time units for making an order of this product")
    ordering_unit = fields.Selection(
        selection=[('days', 'days'),
                   ('weeks', 'weeks'),
                   ('months', 'months'),
                   ('years', 'years')],
        string='Interval unit', required=True, default='months')
    last_order_date = fields.Date(
        string='Last order', help='Date of the last sale order generated')
    specific_price = fields.Float(
        string='Specific price', digits_compute=dp.get_precision('Sale Price'),
        help='Specific price for this product. Keep empty to use the list '
             'price while generating order')
    list_price = fields.Float(
        related='product_id.list_price', string="List price", readonly=True)

    _sql_constraints = [
        ('line_qty_zero', 'CHECK (quantity > 0)',
         'All product quantities must be greater than 0.\n'),
        ('line_interval_zero', 'CHECK (ordering_interval > 0)',
         'All ordering intervals must be greater than 0.\n'),
    ]

    @api.multi
    def onchange_product_id(self, product_id=False):
        result = {}
        if product_id:
            product = self.env['product.product'].browse(product_id)
            if product:
                result['value'] = {'name': product['name']}
        return result


class AgreementRenewal(models.Model):
    _name = 'sale.recurring_orders.agreement.renewal'

    agreement_id = fields.Many2one(
        comodel_name='sale.recurring_orders.agreement',
        string='Agreement reference', ondelete='cascade', select=True)
    date = fields.Date(string='Date', help="Date of the renewal")
    # TODO: Poner estos comentarios editables
    comments = fields.Char(
        string='Comments', size=200, help='Renewal comments')

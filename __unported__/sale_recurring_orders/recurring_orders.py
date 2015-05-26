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

from openerp.osv import osv, fields
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
import openerp.addons.sale
import openerp.netsvc as netsvc

class agreement(osv.osv):
    _name = 'sale.recurring_orders.agreement'
    _inherit = ['mail.thread']
    _description = "Recurring orders agreement"

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
            return date + timedelta(days=interval)
        elif unit == 'weeks':
            return date + timedelta(weeks=interval)
        elif unit == 'months':
            return date + relativedelta(months=interval)
        elif unit == 'years':
            return date + relativedelta(years=interval)
        
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
        'prolong': fields.selection([('recurrent','Renewable fixed term'),('unlimited','Unlimited term'),('fixed','Fixed term')], 'Prolongation', help="Sets the term of the agreement. 'Renewable fixed term': It sets a fixed term, but with possibility of manual renew; 'Unlimited term': Renew is made automatically; 'Fixed term': The term is fixed and there is no possibility to renew.", required=True),
        'end_date': fields.date('End date', help="End date of the agreement"),
        'prolong_interval': fields.integer('Interval', help="Interval in time units to prolong the agreement until new renewable (that is automatic for unlimited term, manual for renewable fixed term)."),
        'prolong_unit': fields.selection([('days','days'),('weeks','weeks'),('months','months'),('years','years')], 'Interval unit', help='Time unit for the prolongation interval'),
        'agreement_line': fields.one2many('sale.recurring_orders.agreement.line', 'agreement_id', 'Agreement lines'),
        'order_line': fields.one2many('sale.recurring_orders.agreement.order', 'agreement_id', 'Order lines', readonly=True),
        'renewal_line': fields.one2many('sale.recurring_orders.agreement.renewal', 'agreement_id', 'Renewal lines', readonly=True),
        'last_renovation_date': fields.date('Last renovation date', help="Last date when agreement was renewed (same as start date if not renewed)"),
        'next_expiration_date': fields.function(__get_next_expiration_date, string='Next expiration date', type='date', method=True, store=True),
        #TODO: Añadir posibilidad de seguir cuando se genera una factura con _track = {}
        'state': fields.selection([('empty', 'Without orders'), ('first', 'First order created'), ('orders', 'With orders')], 'State', readonly=True),
        'renewal_state': fields.selection([('not_renewed', 'Agreement not renewed'), ('renewed', 'Agreement renewed')], 'Renewal state', readonly=True),
        'notes': fields.text('Notes'),
    }

    _defaults = {
        'active': lambda *a: 1,
        'company_id': lambda s, cr, uid, c: s.pool.get('res.company')._company_default_get(cr, uid, 'sale', context=c),
        'prolong': lambda *a: 'unlimited',
        'prolong_interval': lambda *a: 1,
        'prolong_unit': lambda *a: 'years',
        'state': lambda *a: 'empty',
        'renewal_state': lambda *a: 'not_renewed',
    }
    _sql_constraints = [
        ('number_uniq', 'unique(number)', 'Agreement number must be unique !'),
    ]

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
        if not vals.get('start_date'): 
            vals['start_date'] = datetime.now()
        # Set agreement number if empty
        if not vals.get('number'): 
            vals['number'] = self.pool.get('ir.sequence').get(cr, uid, 'sale.r_o.agreement.sequence')
        return super(agreement, self).create(cr, uid, vals, context=context)

    def write(self, cr, uid, ids, vals, context=None):
        value = super(agreement, self).write(cr, uid, ids, vals, context=context)
        # unlink all future orders
        if vals.has_key('active') or vals.has_key('number') or ( vals.has_key('agreement_line') and len(vals['agreement_line']) ) \
            or vals.has_key('prolong') or vals.has_key('end_date') or vals.has_key('prolong_interval') or vals.has_key('prolong_unit'):
            self.unlink_orders(cr, uid, ids, datetime.date(datetime.now()), context)
        return value

    def copy(self, cr, uid, orig_id, default={}, context=None):
        if context is None: context = {}
        agreement_record = self.browse(cr, uid, orig_id)
        default.update({
            'state': 'empty',
            'number': False,
            'active': True,
            'name': '%s*' % agreement_record['name'],
            'start_date': False,
            'order_line': [],
            'renewal_line': [],
        })
        return super(agreement, self).copy(cr, uid, orig_id, default, context)

    def unlink(self, cr, uid, ids, context=None):
        unlink_ids = []
        for agreement in self.browse(cr, uid, ids, context=context):
            confirmedOrders = False
            for order_line in agreement.order_line:
                if order_line.confirmed:
                    confirmedOrders = True
            if not confirmedOrders:
                unlink_ids.append(agreement.id)
            else:
                raise osv.except_osv(_('Invalid action!'), _('You cannot remove agreements with confirmed orders!'))

        self.unlink_orders(cr, uid, unlink_ids, datetime.date(datetime.now()), context=context)
        return osv.osv.unlink(self, cr, uid, unlink_ids, context=context)    

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

    def revise_agreements_expirations_planned(self, cr, uid, context={}):
        """
        Check each active agreement to see if the end is near
        """
        ids = self.search(cr, uid, [])
        revise_ids = []
        for agreement in self.browse(cr, uid, ids, context=context):
            if not agreement.active: continue
            next_expiration_date = datetime.date(datetime.strptime(agreement.next_expiration_date, "%Y-%m-%d"))
            if agreement.prolong == 'unlimited' and next_expiration_date <= datetime.date(datetime.now()):
                # add to a list for reviewing expiration date
                revise_ids.append(agreement.id)
        if revise_ids:
            # force recalculate next_expiration_date
            self.write(cr, uid, revise_ids, {'prolong':'unlimited'}, context=context)
        return True

    def create_order(self, cr, uid, agreement, date, agreement_lines, confirmed_flag, context={}):
        """
        Method that creates an order from given data.
        @param agreement: Agreement method get data from.
        @param date: Date of created order.
        @param agreement_lines: Lines that will generate order lines.
        @confirmed_flag: Confirmed flag in agreement order line will be set to this value.   
        """
        order_obj = self.pool.get('sale.order')
        order_line_obj = self.pool.get('sale.order.line')
        # Create order object
        context['company_id'] = agreement.company_id.id
        order = {
            'date_order': date.strftime('%Y-%m-%d'),
            'date_confirm': date.strftime('%Y-%m-%d'),
            'origin': agreement.number,
            'partner_id': agreement.partner_id.id,
            'state': 'draft',
            'company_id': agreement.company_id.id,
            'from_agreement': True,
        }
        # Get other order values from agreement partner
        order.update(self.pool['sale.order'].onchange_partner_id(cr, uid, [], agreement.partner_id.id,context)['value'])                   
        order['user_id'] = agreement.partner_id.user_id.id
        order_id = order_obj.create(cr, uid, order, context=context)
        # Create order lines objects
        agreement_lines_ids = []
        for agreement_line in agreement_lines:
            order_line = {
                'order_id': order_id,
                'product_id': agreement_line.product_id.id,
                'product_uom_qty': agreement_line.quantity,
                'discount': agreement_line.discount,
            }
            # get other order line values from agreement line product
            order_line.update(self.pool['sale.order.line'].product_id_change(cr, uid, [], order['pricelist_id'], \
                product=agreement_line.product_id.id, qty=agreement_line.quantity, partner_id=agreement.partner_id.id, fiscal_position=1 or order['fiscal_position'])['value'])
            # Put line taxes
            order_line['tax_id'] = [(6, 0, tuple(order_line['tax_id']))]
            # Put custom description
            if agreement_line.additional_description:
                order_line['name'] += " " + agreement_line.additional_description
            order_line_obj.create(cr, uid, order_line, context=context)
            agreement_lines_ids.append(agreement_line.id)
        # Update last order date for lines
        self.pool.get('sale.recurring_orders.agreement.line').write(cr, uid, agreement_lines_ids, {'last_order_date': date.strftime('%Y-%m-%d')} ,context=context)
        # Update agreement state
        if agreement.state != 'orders':
            self.pool.get('sale.recurring_orders.agreement').write(cr, uid, [agreement.id], {'state': 'orders'} ,context=context)
        # Create order agreement record
        agreement_order = {
            'agreement_id': agreement.id,
            'order_id': order_id,
        }
        self.pool.get('sale.recurring_orders.agreement.order').create(cr, uid, agreement_order, context=context)
        
        return order_id

    def _order_created(self, cr, uid, agreement, agreement_lines_ordered, order_id, context={}):
        """
        It triggers actions after order is created.
        This method can be overriden for extending its functionality thanks to its parameters.
        @param agreement: Agreement object whose order has been created
        @param agreement_lines_ordered: List of agreement lines objects used in the creation of the order.
        @param order_id: ID of the created order.  
        """
        pass

    def _order_confirmed(self, cr, uid, agreement, order_id, context={}):
        """
        It triggers actions after order is confirmed.
        This method can be overriden for extending its functionality thanks to its parameters.
        @param agreement: Agreement object whose order has been confirmed
        @param order_id: ID of the confirmed order.
        """
        pass

    def _get_next_order_date(self, agreement, line, startDate, context={}):
        """
        Get next date starting from given date when an order is generated.
        @param line: Agreement line  
        @param startDate: Start date from which next order date is calculated.
        @rtype: datetime
        @return: Next order date starting from the given date.  
        """
        next_date = datetime.strptime(agreement.start_date, '%Y-%m-%d')
        while next_date <= startDate:
            next_date = self.__get_next_term_date(next_date, line.ordering_unit, line.ordering_interval)
        return next_date

    def generate_agreement_orders(self, cr, uid, agreement, startDate, endDate, context={}):
        """
        Check if there is any pending order to create for given agreement. 
        """
        if not agreement.active: return
        
        lines_to_order = {}
        agreement_expiration_date = datetime.strptime(agreement.next_expiration_date, '%Y-%m-%d') 
        if (agreement_expiration_date < endDate) and (agreement.prolong != 'unlimited'): endDate = agreement_expiration_date 
        for line in agreement.agreement_line:
            # Check if there is any agreement line to order 
            if line.active_chk:
                # Check future orders for this line until endDate
                next_order_date = self._get_next_order_date(agreement, line, startDate)
                while next_order_date < endDate:
                    # Add to a list to order all lines together
                    if not lines_to_order.get(next_order_date):
                        lines_to_order[next_order_date] = [] 
                    lines_to_order[next_order_date].append(line)
                    next_order_date = self._get_next_order_date(agreement, line, next_order_date)
        # Order all pending lines
        dates = lines_to_order.keys()
        dates.sort()
        agreement_order_obj = self.pool.get('sale.recurring_orders.agreement.order')
        for date in dates: 
            # Check if an order exists for that date
            if not len(agreement_order_obj.search(cr, uid, [ ('date', '=', str(date)), ('agreement_id', '=', agreement['id']) ])):
                # create it if not exists
                order_id = self.create_order(cr, uid, agreement, date, lines_to_order[date], False, context=context)
                # Call 'event' method
                self._order_created(cr, uid, agreement, lines_to_order, order_id, context=context)

    def generate_initial_order(self, cr, uid, ids, context={}):
        """
        Method that creates an initial order with all the agreement lines
        """
        agreement = self.browse(cr, uid, ids, context=context)[0]
        agreement_lines = []
        # Add only active lines
        for line in agreement.agreement_line:
            if line.active_chk: agreement_lines.append(line)
        order_id = self.create_order(cr, uid, agreement, datetime.strptime(agreement.start_date, '%Y-%m-%d'), agreement_lines, True, context=context)
        # Update agreement state
        self.write(cr, uid, agreement.id, { 'state': 'first' }, context=context)
        # Confirm order
        wf_service = netsvc.LocalService("workflow")
        wf_service.trg_validate(uid, 'sale.order', order_id, 'order_confirm', cr)
        # Get view to show
        data_obj = self.pool.get('ir.model.data')
        result = data_obj._get_id(cr, uid, 'sale', 'view_order_form')
        view_id = data_obj.browse(cr, uid, result).res_id
        # Return view with order created
        return {
            'domain': "[('id','=', " + str(order_id) + ")]",
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'sale.order',
            'context': context,
            'res_id': order_id,
            'view_id': [view_id],
            'type': 'ir.actions.act_window',
            'nodestroy': True
        }

    def generate_next_year_orders_planned(self, cr, uid, context={}):
        """
        Check if there is any pending order to create for each agreement. 
        """
        if context is None: context = {}
        ids = self.search(cr, uid, [('active','=',True)])
        self.generate_next_year_orders(cr, uid, ids, context)

    def generate_next_year_orders(self, cr, uid, ids, context={}):
        """
        Method that generates all the orders of the given agreements for the next year, counting from current date.
        """
        startDate = datetime.now()
        endDate = datetime(startDate.year + 1, startDate.month, startDate.day) 
        for agreement in self.browse(cr, uid, ids, context=context):
            self.generate_agreement_orders(cr, uid, agreement, startDate, endDate, context)
        return True
    
    def confirm_current_orders_planned(self, cr, uid, context={}):
        if context is None: context = {}
        ids = self.search(cr, uid, [])
        now = datetime.now()
        wf_service = netsvc.LocalService("workflow")
        for agreement in self.browse(cr, uid, ids, context=context):
            for agreement_order in agreement.order_line:
                if datetime.strptime(agreement_order['date'], '%Y-%m-%d') <= now and not agreement_order.confirmed:
                    order = agreement_order.order_id
                    if order:
                        wf_service.trg_validate(uid, 'sale.order', order.id, 'order_confirm', cr)
                        self._order_confirmed(cr, uid, agreement, order.id, context)
                        self.pool.get('sale.recurring_orders.agreement.order').write(cr, uid, agreement_order.id, { 'confirmed': 'True' }, context=context)
    
    def unlink_orders(self, cr, uid, ids, startDate, context={}):
        """
        Remove generated orders from given date.
        """
        agreement_order_obj = self.pool.get('sale.recurring_orders.agreement.order')
        ordersToRemove = []
        for agreement in self.browse(cr, uid, ids, context=context):
            for order in agreement['order_line']:
                order_date = datetime.date(datetime.strptime(order['date'], '%Y-%m-%d'))
                if order_date >= startDate and not order.confirmed:
                    if order.order_id.id: ordersToRemove.append(order.order_id.id)
                    agreement_order_obj.unlink(cr, uid, order['id'], context)                    
        self.pool.get('sale.order').unlink(cr, uid, ordersToRemove, context)
    
agreement()

class agreement_line(osv.osv):

    _name = 'sale.recurring_orders.agreement.line'
    _columns = {
        'active_chk': fields.boolean('Active', help='Unchecking this field, this quota is not generated'),
        'agreement_id': fields.many2one('sale.recurring_orders.agreement', 'Agreement reference', ondelete='cascade'),
        'product_id': fields.many2one('product.product', 'Product', ondelete='set null', required=True),
        'name': fields.related('product_id', 'name', type="char", relation='product.product', string='Description', store=False),
        'additional_description': fields.char('Add. description', size=30, help='Additional description that will be added to the product description on orders.'),
        'quantity': fields.float('Quantity', required=True, help='Quantity of the product'),
        'discount': fields.float('Discount (%)', digits=(16, 2)),
        'ordering_interval': fields.integer('Interval', help="Interval in time units for making an order of this product", required=True),
        'ordering_unit': fields.selection([('days','days'),('weeks','weeks'),('months','months'),('years','years')], 'Interval unit', required=True),
        'last_order_date': fields.date('Last order', help='Date of the last sale order generated'),
    }

    _defaults = {
        'active_chk': lambda *a: 1,
        'quantity': lambda *a: 1,
        'ordering_interval': lambda *a: 1,
        'ordering_unit': lambda *a: 'months',
    }

    _sql_constraints = [
        ('line_qty_zero', 'CHECK (quantity > 0)',  'All product quantities must be greater than 0.\n'),
        ('line_interval_zero', 'CHECK (ordering_interval > 0)',  'All ordering intervals must be greater than 0.\n'),
    ]

    def onchange_product_id(self, cr, uid, ids, product_id=False, context={}):
        result = {}
        if product_id:
            product = self.pool.get('product.product').browse(cr, uid, product_id, context=context)
            if product:
                result['value'] = { 'name': product['name'] }
        return result
    
agreement_line()

#TODO: Impedir que se haga doble clic sobre el registro order
class agreement_order(osv.osv):
    """
    Class for recording each order created for each line of the agreement. It keeps only reference to the agreement, not to the line.
    """
    
    def __get_confirm_state(self, cr, uid, ids, field_name, arg, context=None):
        """
        Get confirmed state of the order.
        """
        if not ids: return {}
        res = {}
        for agreement_order in self.browse(cr, uid, ids):
            if agreement_order.order_id:
                res[agreement_order.id] = (agreement_order.order_id.state != 'draft')
        return res

    _name = 'sale.recurring_orders.agreement.order'
    _columns = {
        'agreement_id': fields.many2one('sale.recurring_orders.agreement', 'Agreement reference', ondelete='cascade'),
        'order_id': fields.many2one('sale.order', 'Order', ondelete='cascade'),
        'date': fields.related('order_id', 'date_order', type='date', relation='sale.order', string="Order date", store=False),
        'confirmed': fields.function(__get_confirm_state, string='Confirmed', type='boolean', method=True, store=False),
    }

    def view_order(self, cr, uid, ids, context={}):
        """
        Method for viewing orders associated to an agreement
        """
        agreement_order = self.pool.get('sale.recurring_orders.agreement.order').browse(cr, uid, ids[0], context=context)
        order_id = agreement_order.order_id.id
        # Get view to show
        data_obj = self.pool.get('ir.model.data')
        result = data_obj._get_id(cr, uid, 'sale', 'view_order_form')
        view_id = data_obj.browse(cr, uid, result).res_id
        # Return view with order created
        return {
            #'domain': "[('id','=', " + str(order_id) + ")]",
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'sale.order',
            'context': context,
            'res_id': order_id,
            'view_id': [view_id],
            'type': 'ir.actions.act_window',
            'nodestroy': True
        }

agreement_order()

class agreement_renewal(osv.osv):
    _name = 'sale.recurring_orders.agreement.renewal'
    _columns = {
        'agreement_id': fields.many2one('sale.recurring_orders.agreement', 'Agreement reference', ondelete='cascade', select=True),
        'date': fields.date('Date', help="Date of the renewal"),
        #TODO: Poner estos comentarios editables
        'comments': fields.char('Comments', size=200, help='Renewal comments'),
    }

agreement_renewal()

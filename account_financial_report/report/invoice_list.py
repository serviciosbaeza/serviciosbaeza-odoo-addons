# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2005-2006 TINY SPRL. (http://tiny.be) All Rights Reserved.
#
#    Created by Nicolas Bessi on 13.10.08.
#    Copyright (c) 2008 CamptoCamp. All rights reserved.
#    Copyright (c) 2009 Zikzakmedia S.L. (http://zikzakmedia.com) All Rights Reserved.
#                       Jordi Esteve <jesteve@zikzakmedia.com>
#    Copyright (C) 2012 Pexego Sistemas Informáticos. All Rights Reserved
#                       $Marta Vázquez Rodríguez$
#                       $Omar Castiñeira Saavedra$
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

import time
from mx.DateTime import *
from report import report_sxw
import rml_parse

class print_invoice_list(rml_parse.rml_parse):
    """ Report that print invoices grouped by currency and type """
    _name = 'report.account.print_invoice_list'


    def __init__(self, cr, uid, name, context):
        super(print_invoice_list, self).__init__(cr, uid, name, context)
        #contain tuples of in invoices : (curreny, [browse records], currency_untaxed, currency_tax, currency_total)
        self.in_invoices = []
        #contain tuples of in refunds : (curreny, [browse records], currency_untaxed, currency_tax, currency_total)
        self.in_refunds = []
        #contain tuples of out invoices : (curreny, [browse records], currency_untaxed, currency_tax, currency_total)
        self.out_invoices = []
        #contain tuples of out refunds : (curreny, [browse records], currency_untaxed, currency_tax, currency_total)
        self.out_refunds = []
        self.localcontext.update({
            'time': time,
            'in_invoices': self.in_invoices,
            'in_refunds': self.in_refunds,
            'out_invoices': self.out_invoices,
            'out_refunds': self.out_refunds,
            'detailed_taxes': False,
        })


    def set_context(self, objects, data, ids, report_type = None):
        """We do the grouping and proccessing of invoices"""
        invoice_obj = self.pool.get('account.invoice')
        if data.get('model') and data['model'] == 'ir.ui.menu':
            invoice_types = []
            if data['form']['out_invoice']:
                invoice_types.append('out_invoice')
            if data['form']['out_refund']:
                invoice_types.append('out_refund')
            if data['form']['in_invoice']:
                invoice_types.append('in_invoice')
            if data['form']['in_refund']:
                invoice_types.append('in_refund')
            invoice_states = []
            if data['form']['draft']:
                invoice_states.append('draft')
            if data['form']['proforma']:
                invoice_states.append('proforma')
                invoice_states.append('proforma2')
            if data['form']['open']:
                invoice_states.append('open')
            if data['form']['paid']:
                invoice_states.append('paid')
            if data['form']['cancel']:
                invoice_states.append('cancel')
            where = [('company_id','=',data['form']['company_id'][0]),('type','in',invoice_types),('state','in',invoice_states)]
            if data['form']['state'] in ['byperiod','all']:
                period_ids = data['form']['periods']
                periods = ','.join([str(id) for id in period_ids])
                where.append(('period_id','in',period_ids))
            if data['form']['state'] in ['bydate','all','none']:
                where.append(('date_invoice','>=',data['form']['date_from']))
                where.append(('date_invoice','<=',data['form']['date_to']))
            #print where
            ids = invoice_obj.search(self.cr, self.uid, where)
            objects = invoice_obj.browse(self.cr, self.uid, ids)

            self.localcontext.update({
                'detailed_taxes': data['form'].get('detailed_taxes'),
            })

        if not ids :
            return super(print_invoice_list, self).set_context(objects, data, ids, report_type)
        
        if not isinstance(ids, list) :
            ids = [ids]
        # we create temp list that will be used for store invoices by type
        ininv = []
        outinv = []
        inref = []
        outref = []
        # we get the invoices and sort them by types
        invoices = invoice_obj.browse(self.cr, self.uid, ids)
        for inv in invoices :
            if inv.type == ('in_invoice'):
                ininv.append(inv)
            if inv.type == ('in_refund'):
                inref.append(inv)
            if inv.type == ('out_invoice'):
                outinv.append(inv)
            if inv.type == ('out_refund'):
                outref.append(inv)
        # we process the invoice and attribute them to the property
        order_by = data.get('form') and data.get('form').get('order_by') or None
        self.filter_invoices(ininv, self.in_invoices, order_by)
        self.filter_invoices(outinv, self.out_invoices, order_by)
        self.filter_invoices(inref, self.in_refunds, order_by)
        self.filter_invoices(outref, self.out_refunds, order_by)
        super(print_invoice_list, self).set_context(objects, data, ids, report_type)


    def filter_invoices(self, invoice_list, dest, order_by=None):
        if not invoice_list : return
         
        invoiceByCurrencyList = {}
        #
        # Sort by invoice "number", "date + number" or "partner + reference"
        #
        if order_by=='date':
            invoice_list.sort(key=lambda inv: "%s_%s" % (inv.date_invoice, inv.number))
        elif order_by=='partner':
            invoice_list.sort(key=lambda inv: "%s_%s" % (inv.partner_id and inv.partner_id.name, inv.reference))
        elif order_by=='number':
            invoice_list.sort(key=lambda inv: inv.number)

        #
        # Group by currency
        #
        for invoice in invoice_list:
            currency = invoice.currency_id.name
            if invoiceByCurrencyList.has_key(currency):
                invoiceByCurrencyList[currency].append(invoice)
            else:
                invoiceByCurrencyList[currency] = [invoice]
        #
        # Compute totals for each currency group
        #
        for currency in invoiceByCurrencyList:
            untaxed = tax = total = 0
            taxesTotals = {}
            for invoice in invoiceByCurrencyList[currency]:
                untaxed += invoice.amount_untaxed
                tax += invoice.amount_tax
                total += invoice.amount_total
                for tax_line in invoice.tax_line:
                    if taxesTotals.has_key(tax_line.name):
                        tax_tmp = taxesTotals[tax_line.name]
                    else:
                        tax_tmp = [0.0, 0.0]
                    tax_tmp[0] += tax_line.base_amount
                    tax_tmp[1] += tax_line.tax_amount
                    taxesTotals[tax_line.name] = tax_tmp
            # Unfold taxes totals
            taxesTotalsTuples = []
            tax_keys = taxesTotals.keys()
            tax_keys.sort()
            for tax_key in tax_keys:
                taxesTotalsTuples.append( (tax_key, taxesTotals[tax_key][0], taxesTotals[tax_key][1]) )
            # Append the tuple to the property
            dest.append((currency, invoiceByCurrencyList[currency], untaxed, tax, total, taxesTotalsTuples))
            
        del invoiceByCurrencyList


report_sxw.report_sxw('report.account.invoice.list.report.wzd', 'account.invoice', 'addons/account_financial_report/report/invoice_list.rml', parser=print_invoice_list, header=False)

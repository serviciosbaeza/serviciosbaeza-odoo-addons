# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2014 Serv. Tecnol. Avanzados (http://www.serviciosbaeza.com)
#                       Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>
#    Copyright (c) 2015 Antiun Ingenieria (http://www.antiun.com)
#                       Antonio Espinosa <antonioea@antiun.com>
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
from openerp import fields, models, api
from openerp.addons.decimal_precision import decimal_precision as dp

# Uncomment for debug proposes
# from pprint import pformat
# import logging
# _logger = logging.getLogger(__name__)


class StockPicking(models.Model):
    _inherit = "stock.picking"

    currency_id = fields.Many2one(string='Sale currency',
                                  related='sale_id.currency_id',
                                  store=True, readonly=True)
    amount_untaxed = fields.Float(string='Untaxed amount',
                                  compute='_compute_amounts',
                                  digits=dp.get_precision('Account'),
                                  readonly=True)
    amount_tax = fields.Float(string='Taxes', compute='_compute_amounts',
                              digits=dp.get_precision('Account'),
                              readonly=True)
    amount_total = fields.Float(string='Total', compute='_compute_amounts',
                                digits=dp.get_precision('Account'),
                                readonly=True)

    @api.one
    @api.depends(
        'move_lines.sale_price_subtotal',
        'move_lines.procurement_id.sale_line_id.tax_id',
        'move_lines.procurement_id.sale_line_id.order_id.partner_id',
    )
    def _compute_amounts(self):
        untaxed = 0.0
        for move in self.move_lines:
            untaxed += move.sale_price_subtotal

        tax = 0.0
        for move in self.move_lines:
            if not (move.procurement_id and
                    move.procurement_id.sale_line_id):
                continue
            sale_line = move.procurement_id.sale_line_id
            price_unit = (move.sale_price_unit *
                          (100 - move.sale_discount or 0.0) / 100.0)
            for c in sale_line.tax_id.compute_all(price_unit,
                                      move.product_qty,
                                      move.product_id,
                                      sale_line.order_id.partner_id)['taxes']:
                tax += c.get('amount', 0.0)
        currency = self.currency_id
        if currency:
            tax = currency.round(tax)

        self.amount_untaxed = untaxed
        self.amount_tax = tax
        self.amount_total = untaxed + tax

# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Jacques-Etienne Baudoux <je@bcim.be>
#    Copyright 2016 BCIM sprl, Camptocamp
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
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

from datetime import date, timedelta

from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
import openerp.addons.decimal_precision as dp
from openerp import fields, models, api


class ProductProduct(models.Model):
    _inherit = 'product.product'

    stat_amount_deliveries = fields.Integer(
        'Amount of Deliveries',
        help="Mean amount of customer deliveries on the last 6 months",
        compute='_get_stat_amount_deliveries',
        store=True)

    @api.one
    def _get_stat_amount_deliveries(self):
        duration = 6 * 30
        start_date = (date.today() - timedelta(days=duration)).strftime(
            DEFAULT_SERVER_DATETIME_FORMAT)
        customer_loc = self.env.ref('stock.stock_location_customers')
        self.stat_amount_deliveries = self.env['stock.move'].search_count([
            ('date', '>=', start_date),
            ('product_id', '=', self.id),
            ('state', 'not in', ('draft', 'cancel')),
            ('location_dest_id', '=', customer_loc.id),
            ]) / duration

    stat_qty_delivered = fields.Integer(
        'Mean Qty Delivered',
        help="Mean Quantity delivered on the last 30 days",
        compute='_get_stat_qty_delivered',
        store=True)

    @api.one
    def _get_stat_qty_delivered(self):
        duration = 30
        start_date = (date.today() - timedelta(days=duration)).strftime(
            DEFAULT_SERVER_DATETIME_FORMAT)
        customer_loc = self.env.ref('stock.stock_location_customers')
        self.stat_amount_deliveries = sum(self.env['stock.move'].search([
            ('date', '>=', start_date),
            ('product_id', '=', self.id),
            ('state', 'not in', ('draft', 'cancel')),
            ('location_dest_id', '=', customer_loc.id),
            ]).mapped('product_qty')) / duration

    qty_in_parking = fields.Float(
        'Qty in parking',
        digits=dp.get_precision('Product Unit of Measure'),
        compute='_get_qty_in_parking')
    qty_in_reserve = fields.Float(
        'Qty in reserve',
        digits=dp.get_precision('Product Unit of Measure'),
        compute='_get_qty_in_reserve')
    qty_in_bin = fields.Float(
        'Qty in bins',
        digits=dp.get_precision('Product Unit of Measure'),
        compute='_get_qty_in_bin')

    @api.one
    def _get_qty_in_parking(self):
        parking_ids = self.env['stock.location'].search(
            [('kind', '=', 'parking')]).ids
        self.qty_in_parking = parking_ids and self.with_context(
            location=parking_ids).qty_available or 0

    @api.one
    def _get_qty_in_reserve(self):
        reserve_ids = self.env['stock.location'].search(
            [('kind', '=', 'reserve')]).ids
        self.qty_in_reserve = reserve_ids and self.with_context(
            location=reserve_ids).qty_available or 0

    @api.one
    def _get_qty_in_bin(self):
        reserve_ids = self.env['stock.location'].search(
            [('kind', '=', 'bin')]).ids
        self.qty_in_bin = reserve_ids and self.with_context(
            location=reserve_ids).qty_available or 0

    move_ids = fields.One2many(
        'stock.move', 'product_id',
        'Moves')
    priority_arrangement = fields.Integer(
        'Arrangement Priority',
        compute='_get_refill_priority',
        store=True)
    priority_reassort = fields.Integer(
        'Reassortment Priority',
        compute='_get_refill_priority',
        store=True)

    @api.one
    @api.depends('stat_amount_deliveries', 'move_ids.state')
    def _get_refill_priority(self):
        """ Compute how important it is to refill the bin """
        # il faut calculer combien de temps on tient en tenant compte d'une
        # consommation moyenne de 1,6 (=2)
        """ How often the product is taken in a bin, how important it is to
        arrange. This is divided by the quantity already arranged. """
        qty_moves = self.stat_amount_deliveries

        qty_in_stock = (self.qty_in_bin + self.qty_in_reserve)
        if ((qty_in_stock - self.outgoing_qty) < 0):
            # we will be out of stock
            prio = 1000 + min(999, qty_moves)
        else:
            # IMP-TODO: we could compute how many days we can survive according
            # to the mean consumption
            prio = min(999, qty_moves / max(1, qty_in_stock))
        self.priority_arrangement = prio

        # min = mean consumption on the month
        qty_in_stock = self.qty_in_bin
        prio = 0
        if (qty_in_stock - self.stat_qty_delivered) <= 0:
            # probability to be out of stock. Amount of moves increase priority
            prio = min(999, qty_moves * 10)
        if ((qty_in_stock - self.outgoing_qty) < 0):
            # we will be out of stock
            prio += 2000
        self.priority_reassort = prio

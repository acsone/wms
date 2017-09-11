# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Jacques-Etienne Baudoux <je@bcim.be>
#    Copyright 2016-2017 BCIM sprl, Camptocamp
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

from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
import odoo.addons.decimal_precision as dp
from odoo import fields, models, api


class ProductProduct(models.Model):
    _inherit = 'product.product'

    stat_amount_deliveries = fields.Integer(
        'Amount of Deliveries',
        help="Mean amount of customer deliveries on the last 6 months",
        compute='_get_stat_amount_deliveries')

    @api.multi
    def _get_stat_amount_deliveries(self):
        duration = 6 * 30
        start_date = (date.today() - timedelta(days=duration)).strftime(
            DEFAULT_SERVER_DATETIME_FORMAT)
        customer_loc = self.env.ref('stock.stock_location_customers')

        for product in self:
            product.stat_amount_deliveries = \
                self.env['stock.move'].search_count([
                    ('date', '>=', start_date),
                    ('product_id', '=', product.id),
                    ('state', 'not in', ('draft', 'cancel')),
                    ('location_dest_id', '=', customer_loc.id),
                ]) / duration

    stat_qty_delivered = fields.Integer(
        'Mean Qty Delivered',
        help="Mean Quantity delivered on the last 30 days",
        compute='_get_stat_qty_delivered')

    @api.multi
    def _get_stat_qty_delivered(self):
        duration = 30
        start_date = (date.today() - timedelta(days=duration)).strftime(
            DEFAULT_SERVER_DATETIME_FORMAT)
        customer_loc = self.env.ref('stock.stock_location_customers')

        for product in self:
            product.stat_amount_deliveries = \
                sum(self.env['stock.move'].search([
                    ('date', '>=', start_date),
                    ('product_id', '=', product.id),
                    ('state', 'not in', ('draft', 'cancel')),
                    ('location_dest_id', '=', customer_loc.id),
                ]).mapped('product_qty')) / duration

    @api.multi
    def _get_domain_locations(self):
        """ Add possibility to filter by kind of location when
        computing qty_available
        """
        loc_domain = super(ProductProduct, self)._get_domain_locations()
        kind = self._context.get('loc_kind')
        if kind:
            loc_domain = (
                ['&', ('location_id.kind', '=', kind)] + loc_domain[0],
                ['&', ('location_id.kind', '=', kind)] + loc_domain[1],
                ['&', ('location_id.kind', '=', kind)] + loc_domain[2],
            )
        return loc_domain

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
        _self = self.with_context(loc_kind='parking')
        self.qty_in_parking = _self.qty_available or 0

    @api.one
    def _get_qty_in_reserve(self):
        _self = self.with_context(loc_kind='reserve')
        self.qty_in_reserve = _self.qty_available or 0

    @api.one
    def _get_qty_in_bin(self):
        self.qty_in_bin = self.with_context(loc_kind='bin').qty_available or 0

    move_ids = fields.One2many(
        'stock.move', 'product_id',
        'Moves')
    priority_arrangement = fields.Integer(
        'Arrangement Priority')
    priority_reassort = fields.Integer(
        'Reassortment Priority')

    @api.multi
    def _compute_refill_priority(self):
        """ Compute how important it is to refill the bin.
        How often the product is taken in a bin, how important it is to
        arrange. This is divided by the quantity already arranged. """
        for product in self:
            qty_moves = product.stat_amount_deliveries
            days_to_cover = 2

            qty_in_stock = (product.qty_in_bin + product.qty_in_reserve)
            stat_qty_delivered = product.stat_qty_delivered

            if (qty_in_stock - product.outgoing_qty) < 0:
                # we will be out of stock
                prio = 2000 + min(999, qty_moves)
            elif (qty_in_stock - stat_qty_delivered * days_to_cover) < 0:
                # probability to be out of stock.
                # Amount of moves increase priority
                prio = 1000 + min(999, qty_moves)
            else:
                prio = min(999, qty_moves / max(1, qty_in_stock))
            product.priority_arrangement = prio

            # min = mean consumption on the month
            qty_in_stock = product.qty_in_bin
            if ((qty_in_stock - product.outgoing_qty) < 0):
                # we will be out of stock
                prio = 2000 + min(999, qty_moves)
            elif (qty_in_stock - stat_qty_delivered * days_to_cover) < 0:
                # probability to be out of stock.
                # Amount of moves increase priority
                prio = 1000 + min(999, qty_moves)
            else:
                prio = 0
            product.priority_reassort = prio

    @api.model
    def cron_compute_refill_priority(self):
        """
        This method will compute the refill priority on a set of products
        :return:
        """
        # TODO This search can be improved if the cron take too much time
        products = self.search([])
        products._compute_refill_priority()

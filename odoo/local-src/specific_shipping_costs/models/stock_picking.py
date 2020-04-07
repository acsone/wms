# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import api, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def _add_delivery_cost_to_so(self):
        """Fee line for specific shipping cost is added when round is done"""
        if (
            self.carrier_id.use_specific_cost_calculation
            or not self.carrier_price
        ):
            return
        return super(StockPicking, self)._add_delivery_cost_to_so()

    @api.multi
    def do_transfer(self):
        self.check_shipping_cost()
        return super(StockPicking, self).do_transfer()

    @api.multi
    def check_shipping_cost(self):
        """Compute shipping costs for the customers in the delivery round"""
        self.ensure_one()
        if self.picking_type_code != "outgoing":
            return
        moves = (
            self.mapped('delivery_round_id.shipping_ids')
            .filtered(lambda ship: ship.partner_id == self.partner_id)
            .mapped('move_lines')
        )
        moves = moves.filtered(lambda m: m.state in ('assigned', 'done'))
        round_saleorders = moves.mapped('procurement_id.sale_line_id.order_id')
        round_carriers = round_saleorders.mapped('carrier_id').filtered(
            lambda r: r.use_specific_cost_calculation
        )
        if len(round_carriers) == 0:
            # No delivery carrier that use specific shipping cost so out.
            return
        round_customers = round_saleorders.mapped('partner_id').filtered(
            lambda r: r.help_with_fee is True
        )
        for customer in round_customers:
            # Get all sale order used to compute fee for a customer it is not
            # only the sale orders in the round but all the one that have not
            # yet been used to compute those costs.

            customer_round_saleorders = round_saleorders.filtered(
                lambda r: r.partner_id == customer
            )
            customer_carriers = customer_round_saleorders.mapped('carrier_id')

            for delivery_carrier in customer_carriers:
                self.env['sale.order'].charge_shipping_costs_by_carrier(
                    delivery_carrier, customer_round_saleorders, customer
                )

# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo.addons.stock.models.stock_picking import Picking


class StockPicking(Picking):
    def _add_delivery_cost_to_so(self):
        """Fee line for specific shipping cost is added when round is done."""
        if (
            self.picking_type_id.avoid_shipping_cost
            and self.picking_type_code == "outgoing"
        ):
            return None
        if self.carrier_id.use_specific_cost_calculation or not self.carrier_price:
            return None
        res = super()._add_delivery_cost_to_so()
        # check if a delivery line has been added by super and set the price if so
        sale_order = self.sale_id
        delivery_line = sale_order.order_line.filtered(
            lambda l: l.is_delivery
            and l.currency_id.is_zero(l.price_unit)
            and l.product_id == self.carrier_id.product_id
        )
        if delivery_line:
            delivery_line.price_unit = self.carrier_price
            delivery_line.name = (
                f"{sale_order.carrier_id.name}: "
                f"{sale_order.carrier_id.product_id.description_sale}"
                if sale_order.carrier_id.product_id.description_sale
                else sale_order.carrier_id.name
            )
        return res

    def _action_done(self):
        for rec in self:
            rec._check_shipping_cost()
        return super()._action_done()

    def _check_shipping_cost(self):
        """Compute shipping costs for the customers in the release channel."""
        self.ensure_one()
        if (
            self.picking_type_code != "outgoing"
            or self.picking_type_id.avoid_shipping_cost
            or not self.carrier_id.use_specific_cost_calculation
        ):
            return
        # Don't use the picking_ids on release_channel_id field as this
        # will retrieve the whole world pickings for that release channel
        # Instead take all release channel to plan pickings (if not already shipped)
        # in addition with those that are in shipment advice
        pickings = self.release_channel_id.picking_to_plan_ids
        pickings |= self.planned_shipment_advice_id.loaded_picking_ids
        moves = pickings.filtered(
            lambda ship: ship.partner_id == self.partner_id
        ).mapped("move_ids")
        moves = moves.filtered(lambda m: m.state in ("assigned", "done"))
        round_saleorders = moves.mapped("sale_line_id.order_id")
        round_carriers = round_saleorders.mapped("carrier_id").filtered(
            lambda r: r.use_specific_cost_calculation
        )
        if len(round_carriers) == 0:
            # No delivery carrier that use specific shipping cost so out.
            return
        round_customers = round_saleorders.mapped("partner_id").filtered(
            lambda r: r.help_with_fee is True or r.help_with_fixed_fee is True
        )
        for customer in round_customers:
            # Get all sale order used to compute fee for a customer it is not
            # only the sale orders in the round but all the one that have not
            # yet been used to compute those costs.

            customer_round_saleorders = round_saleorders.filtered(
                lambda r, c=customer: r.partner_id == c
            )
            customer_carriers = customer_round_saleorders.mapped("carrier_id")
            for delivery_carrier in customer_carriers:
                self.env["sale.order"].charge_shipping_costs_by_carrier(
                    delivery_carrier, customer_round_saleorders, customer
                )

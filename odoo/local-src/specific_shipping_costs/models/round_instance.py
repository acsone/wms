# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import _, api, models


class RoundInstance(models.Model):
    _inherit = 'round.instance'

    @api.multi
    def button_done(self):
        self.ensure_one()
        res = super(RoundInstance, self).button_done()
        self.check_shipping_cost()
        return res

    @api.multi
    def _deliver(self, background=True):
        """ Override with check_shipping_cost to add fees on shipping invoice.
        """
        self.ensure_one()
        self.check_shipping_cost()
        res = super(RoundInstance, self)._deliver(background=background)
        return res

    @api.multi
    def check_shipping_cost(self):
        """Compute shipping costs for the customers in the delivery round"""
        self.ensure_one()
        moves = self.shipping_ids.mapped('move_lines')
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
            sale_orders = self.env['sale.order'].search(
                [
                    ('partner_id', '=', customer.id),
                    ('state', '!=', 'cancel'),
                    ('used_for_delivery_fee', '=', False),
                    ('carrier_id', 'in', round_carriers.ids),
                ]
            )
            customer_round_saleorders = round_saleorders.filtered(
                lambda r: r.partner_id == customer
            )
            customer_carriers = customer_round_saleorders.mapped('carrier_id')

            for delivery_carrier in customer_carriers:
                self.env['round.instance'].charge_shipping_costs_by_carrier(
                    delivery_carrier,
                    customer_round_saleorders,
                    sale_orders,
                    customer,
                )

    @api.model
    def charge_shipping_costs_by_carrier(
        self, carrier, round_saleorders, sale_orders, customer
    ):
        """Check customer fee for one delivery carrier.

        And charge the customer on his last sale order if nececssary.
        """

        sale_orders = sale_orders.filtered(lambda r: r.carrier_id == carrier)
        sum_ordered = sum(sale_orders.mapped('amount_untaxed'))
        sale_orders.write({'used_for_delivery_fee': True})

        if (
            sum_ordered >= carrier.amount
            or sum_ordered == 0
            or not carrier.fixed_price
        ):
            return
        # Find the last sale order passed and charge the customer
        so = round_saleorders.filtered(
            lambda r: r.partner_id == customer and r.carrier_id == carrier
        ).sorted(key=lambda r: r.id, reverse=True)[0]
        so.sudo().write(
            {
                'order_line': [
                    (
                        0,
                        0,
                        {
                            'name': _('Shipping cost'),
                            'product_id': carrier.product_id.id,
                            'product_uom_qty': 1,
                            'price_unit': carrier.fixed_price,
                            'is_delivery': True,
                        },
                    )
                ]
            }
        )

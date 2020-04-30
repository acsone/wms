# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    used_for_delivery_fee = fields.Boolean(
        'Has been used for delivery fee calculation', copy=False
    )

    @api.model
    def charge_shipping_costs_by_carrier(
        self, carrier, round_saleorders, customer
    ):
        """Check customer fee for one delivery carrier.

        And charge the customer on his last sale order if nececssary.
        """
        if not carrier.fixed_price:
            return
        sale_orders = self.search(
            [
                ('partner_id', '=', customer.id),
                ('state', '!=', 'cancel'),
                ('used_for_delivery_fee', '=', False),
                ('carrier_id', '=', carrier.id),
            ]
        )
        if not sale_orders:
            return
        sum_ordered = sum(sale_orders.mapped('amount_untaxed'))
        sale_orders.write({'used_for_delivery_fee': True})
        if sum_ordered == 0 or sum_ordered >= carrier.amount:
            return
        # Find the last sale order passed and charge the customer
        round_saleorders = round_saleorders.filtered(
            lambda r: r.carrier_id == carrier
        ).sorted(key=lambda r: r.id, reverse=True)[0]
        for order in round_saleorders.sudo():
            order._create_delivery_line(carrier, carrier.fixed_price)

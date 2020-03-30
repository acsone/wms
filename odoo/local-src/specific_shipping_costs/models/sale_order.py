# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import _, api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    used_for_delivery_fee = fields.Boolean(
        'Has been used for delivery fee calculation'
    )

    @api.model
    def charge_shipping_costs_by_carrier(
        self, carrier, round_saleorders, customer
    ):
        """Check customer fee for one delivery carrier.

        And charge the customer on his last sale order if nececssary.
        """
        sale_orders = self.search(
            [
                ('partner_id', '=', customer.id),
                ('state', '!=', 'cancel'),
                ('used_for_delivery_fee', '=', False),
                ('carrier_id', 'in', carrier.ids),
            ]
        )

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
        round_saleorders = round_saleorders.filtered(
            lambda r: r.carrier_id == carrier
        ).sorted(key=lambda r: r.id, reverse=True)[0]
        round_saleorders.sudo().write(
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

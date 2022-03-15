# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    used_for_delivery_fee = fields.Boolean(
        "Has been used for delivery fee calculation", copy=False
    )

    @api.model
    def charge_shipping_costs_by_carrier(self, carrier, round_saleorders, customer):
        """Check customer fee for one delivery carrier.

        And charge the customer on his last sale order if nececssary.
        """
        if not carrier.fixed_price:
            return
        # this query checks all existing SOs for the customer, which might be massive if
        # his 'help_with_fee' setting has been changed overnight.
        # in particular the SQL write allows to skip triggering an export to the ESB
        # for each historical SO
        query_args = (customer.id, carrier.id)
        query_select = """SELECT amount_untaxed FROM sale_order
        WHERE partner_id = %s AND state != 'cancel'
        AND used_for_delivery_fee = false AND carrier_id = %s;
        """
        self.env.cr.execute(query_select, query_args)
        result = self.env.cr.fetchall()
        if not result:
            return
        sum_ordered = sum(r[0] for r in result)
        query_update = """UPDATE sale_order SET used_for_delivery_fee = true
        WHERE partner_id = %s AND state != 'cancel'
        AND used_for_delivery_fee = false AND carrier_id = %s;
        """
        self.env.cr.execute(query_update, query_args)
        if sum_ordered == 0 or sum_ordered >= carrier.amount:
            return
        # Find the last sale order passed and charge the customer
        round_saleorders = round_saleorders.filtered(
            lambda r: r.carrier_id == carrier
        ).sorted(key=lambda r: r.id, reverse=True)[0]
        for order in round_saleorders.sudo():
            order._create_delivery_line(carrier, carrier.fixed_price)

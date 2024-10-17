# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from odoo import api, fields

from odoo.addons.sale.models import sale_order


class SaleOrder(sale_order.SaleOrder):

    used_for_delivery_fee = fields.Boolean(
        "Has been used for delivery fee calculation", copy=False
    )
    used_for_fixed_fee = fields.Boolean(
        "Has been used for fixed delivery fee calculation", copy=False
    )
    fixed_extra_fee_for_delivery = fields.Float(
        string="Fixed extra fee", compute="_compute_fixed_extra_fee_for_delivery"
    )

    @api.depends("carrier_id")
    def _compute_fixed_extra_fee_for_delivery(self):
        for rec in self:
            if not rec.carrier_id:
                rec.fixed_extra_fee_for_delivery = 0.0
                continue
            rec.fixed_extra_fee_for_delivery = rec.carrier_id.fixed_fee_for_delivery

    @api.model
    def charge_shipping_costs_by_carrier(self, carrier, round_saleorders, customer):
        """Check customer fee for one delivery carrier.

        And charge the customer on his last sale order if nececssary.
        """
        fixed_delivery_fee = carrier.fixed_fee_for_delivery
        extra_delivery_fee = carrier.fixed_price

        if customer.help_with_fee and extra_delivery_fee:
            self.charge_extra_fees_on_customer(
                round_saleorders,
                customer,
                carrier,
                extra_delivery_fee,
                "used_for_delivery_fee",
            )
        if customer.help_with_fixed_fee and fixed_delivery_fee:
            self.charge_extra_fees_on_customer(
                round_saleorders,
                customer,
                carrier,
                fixed_delivery_fee,
                "used_for_fixed_fee",
            )

    def _check_charge_fee(self, carrier, sum_ordered, used_to_charge_delivery_fee):
        if used_to_charge_delivery_fee == "used_for_fixed_fee":
            do_not_charge_fee = not sum_ordered
        if used_to_charge_delivery_fee == "used_for_delivery_fee":
            do_not_charge_fee = not sum_ordered or sum_ordered >= carrier.amount
        return do_not_charge_fee

    def charge_extra_fees_on_customer(
        self, round_saleorders, customer, carrier, fee, used_to_charge_delivery_fee
    ):
        # this query checks all existing SOs for the customer, which might be massive if
        # his 'help_with_fee' setting has been changed overnight.
        # in particular the SQL write allows to skip triggering an export to the ESB
        # for each historical SO
        query_args = (customer.id, carrier.id)
        if used_to_charge_delivery_fee == "used_for_delivery_fee":
            # Filter out sale orders with a delivery line already
            round_saleorders = round_saleorders.filtered(
                lambda r: r.carrier_id == carrier and not r.used_for_delivery_fee
            )
            query_select = """SELECT amount_untaxed FROM sale_order
            WHERE partner_id = %s AND state in ('sale', 'done')
            AND (used_for_delivery_fee = false OR used_for_delivery_fee is NULL)
            AND carrier_id = %s;
            """
            self.env.cr.execute(query_select, query_args)
            result = self.env.cr.fetchall()
            if not result:
                return

            sum_ordered = sum(r[0] for r in result)
            query_update = """UPDATE sale_order SET used_for_delivery_fee = true
            WHERE partner_id = %s AND state in ('sale', 'done')
            AND (used_for_delivery_fee = false OR used_for_delivery_fee is NULL)
            AND carrier_id = %s;
            """
            self.env.cr.execute(query_update, query_args)

        if used_to_charge_delivery_fee == "used_for_fixed_fee":
            # Filter out sale orders with a delivery line already
            round_saleorders = round_saleorders.filtered(
                lambda r: r.carrier_id == carrier and not r.used_for_fixed_fee
            )

            query_select = """SELECT amount_untaxed FROM sale_order
            WHERE partner_id = %s AND state in ('sale', 'done')
            AND (used_for_fixed_fee = false OR used_for_fixed_fee is NULL)
            AND carrier_id = %s;
            """
            self.env.cr.execute(query_select, query_args)
            result = self.env.cr.fetchall()
            if not result:
                return

            sum_ordered = sum(r[0] for r in result)
            query_update = """UPDATE sale_order SET used_for_fixed_fee = true
            WHERE partner_id = %s AND state in ('sale', 'done')
            AND (used_for_fixed_fee = false OR used_for_fixed_fee is NULL)
            AND carrier_id = %s;
            """
            self.env.cr.execute(query_update, query_args)

        do_not_charge_fee = self._check_charge_fee(
            carrier, sum_ordered, used_to_charge_delivery_fee
        )
        if do_not_charge_fee:
            return

        if round_saleorders:
            round_saleorders = round_saleorders.filtered(
                lambda r: r.carrier_id == carrier
            ).sorted(key=lambda r: r.id, reverse=True)[0]
            for order in round_saleorders.sudo():
                order._create_delivery_line(carrier, fee)

# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class RoundInstance(models.Model):

    _inherit = "round.instance"

    @api.multi
    def _get_sorted_shipping_ids(self):
        """
        return the shippings into the expected delivery order
        """
        self.ensure_one()
        shipping_ranked = super(RoundInstance, self)._get_sorted_shipping_ids()

        def comparer(left, right):
            # First priority : sort by rank
            if left.rank > right.rank:
                return 1
            if left.rank == right.rank:
                # Same rank -- second priority: sort by vet name
                if left.partner_id.name > right.partner_id.name:
                    return 1
                # Same partner id : one is a b2c customer
                if left.partner_id.name == right.partner_id.name:
                    # 2 b2c for the same vet -- sort them by name
                    if (
                        left.customer_id.is_b2c_customer
                        and right.customer_id.is_b2c_customer
                    ):
                        return cmp(  # pylint: disable=undefined-variable
                            left.customer_id.name, right.customer_id.name
                        )
                    if (
                        left.customer_id.is_b2c_customer
                        and not right.customer_id.is_b2c_customer
                    ):
                        return 1
                    return -1
                return -1
            return -1

        sorted_shipping_list = sorted(shipping_ranked, cmp=comparer)
        ids = [ship.id for ship in sorted_shipping_list]

        return self.env["stock.picking"].browse(ids)

    @api.multi
    def print_all_deliveryslip(self):
        super(RoundInstance, self).print_all_deliveryslip()
        shipping_done = self._get_sorted_shipping_ids()
        return self.env["report"].get_action(shipping_done, "stock.report_deliveryslip")

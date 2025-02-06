# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from collections import defaultdict

from odoo import models


class SaleOrder(models.Model):

    _inherit = "sale.order"

    def _get_order_line_price(self, order_line, price_type):
        if self.env.context.get("is_rebate"):
            price_type = "price_subtotal"
        return super()._get_order_line_price(order_line, price_type)

    def _program_check_compute_points(self, programs):
        rebate_programs = programs.filtered(
            lambda p: p.program_type == "year_end_rebate"
        )
        other_programs = programs - rebate_programs
        result = {}
        if other_programs:
            result = super()._program_check_compute_points(other_programs)
        if rebate_programs:
            # We need to say that we are in a rebate context to compute the points
            # with the price_subtotal instead of the price_unit
            rebate_result = super(
                SaleOrder, self.with_context(is_rebate=True)
            )._program_check_compute_points(rebate_programs)
            result.update(rebate_result)
        return result

    def _get_claimable_rewards(self, forced_coupons=None):
        # rebate rewards are not claimable
        result = super()._get_claimable_rewards(forced_coupons=forced_coupons)
        filtered_result = defaultdict(lambda: self.env["loyalty.reward"])
        for coupon, rewards in result.items():
            for reward in rewards:
                if reward.reward_type != "rebate":
                    filtered_result[coupon] += reward
        return filtered_result

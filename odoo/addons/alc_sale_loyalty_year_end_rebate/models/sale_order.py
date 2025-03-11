# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from collections import defaultdict

from odoo import _, fields, models

from odoo.addons.queue_job.delay import chain


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

    def _get_program_domain(self):
        domain = super()._get_program_domain()
        new_domain = []
        if self.env.context.get("ensure_program_valid_at_order_date"):
            for leaf in domain:
                if len(leaf) != 3:
                    new_domain.append(leaf)
                    continue
                field, operator, value = leaf
                if field in ("date_from", "date_to") and not isinstance(value, bool):
                    value = (
                        self.date_order
                        if self.date_order
                        else fields.Date.context_today(self)
                    )
                new_domain.append((field, operator, value))
            domain = new_domain
        program_ids = self.env.context.get("restricted_program_ids")
        if program_ids:
            domain.append(("id", "in", program_ids))
        return domain

    def _recompute_rfa(self, programs):
        """Recompute the RFA for the partner."""
        if not programs:
            return
        programs = programs.filtered(lambda p: p.program_type == "year_end_rebate")
        for order in self.with_context(
            ensure_program_valid_at_order_date=True,
            restricted_program_ids=programs.ids,
        ):
            # when the order is already confirmed and coupon points are
            # already created, we need to remove the points from the card
            # before recomputing the RFA since even if the coupon points
            # are updated, the card points are not updated. This is because
            # the coupon points are added to the card points only when the
            # order is confirmed or when the coupon points are created.
            # So we update the card points and unlink the coupon points
            # before recomputing the RFA. If new coupon points are created
            # they will be added to the card points at creation time.
            if order.state in ["sale", "done"] and order.coupon_point_ids:
                for coupon, changes in order._get_point_changes().items():
                    coupon.points -= changes
            order.coupon_point_ids.unlink()
            order._update_programs_and_rewards()

    def _delay_recompute_rfa(self, programs, batch_size=10):
        """Delay the recomputation of the RFA for the partner."""
        if not programs:
            return
        programs = programs.filtered(lambda p: p.program_type == "year_end_rebate")
        # to avoid concurrent update issues we need to partition the orders by beneficiary
        # and chain the recomputation by beneficiary. In this way we run the recomputation
        # sequentially for each beneficiary but in parallel for different beneficiaries
        for program in programs:
            for beneficiary, orders in self.partition(
                lambda so, program=program: so._get_beneficiary_partner_for_loyalty_program(
                    program
                )
            ).items():
                batches = [orders]
                total = len(orders)
                step = 0
                if batch_size:
                    batches = list(orders.batch(batch_size))
                jobs = []
                for batch in batches:
                    next_step = len(batch) + step
                    description = _(
                        "Recompute RFA for %(beneficiary)s from %(from_)s to %(to)s on %(total)s orders",
                        beneficiary=beneficiary.name,
                        from_=step,
                        to=next_step,
                        total=total,
                    )
                    delayable = (
                        batch.delayable()
                        .set(description=description)
                        ._recompute_rfa(programs)
                    )
                    jobs.append(delayable)
                chain(*jobs).delay()

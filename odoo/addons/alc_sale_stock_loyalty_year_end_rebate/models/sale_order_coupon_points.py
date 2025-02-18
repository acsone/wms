# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleOrderCouponPoints(models.Model):
    _inherit = "sale.order.coupon.points"

    accrued_points = fields.Float(default=0.0)

    max_accrued_points = fields.Float(
        help="The maximum amount of points that can be earned with the SO "
        "if all the rules have overperformed.",
        default=0.0,
    )

    def _partition_by_order_id_and_program_id(self):
        coupon_points_by_order_and_program = {}
        program_ids = set()
        order_ids = set()
        for coupon_points in self:
            loyalty_card = coupon_points.coupon_id
            if not loyalty_card.program_type == "year_end_rebate":
                continue
            key = (coupon_points.order_id.id, loyalty_card.program_id.id)
            coupon_points_by_order_and_program[key] = coupon_points
            program_ids.add(loyalty_card.program_id.id)
            order_ids.add(coupon_points.order_id.id)
        return coupon_points_by_order_and_program, program_ids, order_ids

    def _refresh_accrued_points(self):
        coupon_points_by_order_and_program, program_ids, order_ids = (
            self._partition_by_order_id_and_program_id()
        )
        self.env["sale.order.line"].flush_model(
            ["qty_delivered", "price_subtotal", "product_id", "order_id"]
        )
        if order_ids:
            sql = """
                SELECT
                    sol.order_id,
                    lc.program_id,
                    sum(sol.price_subtotal / sol.product_uom_qty * sol.qty_delivered * lr.reward_point_amount),
                    sum(sol.price_subtotal / sol.product_uom_qty * sol.qty_delivered * COALESCE(NULLIF(lr.reward_point_max_amount, 0), lr.reward_point_amount) )
                FROM
                    sale_order_line sol,
                    sale_order_coupon_points scp,
                    loyalty_rule_product_product_rel lrpp,
                    loyalty_rule lr,
                    loyalty_card lc
                WHERE
                    scp.order_id = sol.order_id
                    AND lrpp.product_product_id=sol.product_id
                    AND lr.id = lrpp.loyalty_rule_id
                    AND lr.program_id = lc.program_id
                    AND lc.id = scp.coupon_id
                    AND lc.program_id in %(program_id)s
                    AND sol.order_id in %(order_id)s
                GROUP BY sol.order_id, lc.program_id;
            """
            self.env.cr.execute(
                sql, {"program_id": tuple(program_ids), "order_id": tuple(order_ids)}
            )
            for order_id, program_id, points, max_points in self.env.cr.fetchall():
                coupon_point = coupon_points_by_order_and_program.pop(
                    (order_id, program_id)
                )
                old_value = coupon_point.accrued_points
                new_value = points
                if old_value != new_value:
                    coupon_point.coupon_id.accrued_points -= old_value
                    coupon_point.coupon_id.accrued_points += new_value
                    coupon_point.accrued_points = new_value
                old_max_value = coupon_point.max_accrued_points
                new_max_value = max_points
                if old_max_value != new_max_value:
                    coupon_point.coupon_id.max_accrued_points -= old_max_value
                    coupon_point.coupon_id.max_accrued_points += new_max_value
                    coupon_point.max_accrued_points = new_max_value

        # Reset the remaining coupon points since they are no values for them
        for coupon_point in coupon_points_by_order_and_program.values():
            coupon_point.coupon_id.accrued_points -= coupon_point.accrued_points
            coupon_point.accrued_points = 0.0
            coupon_point.coupon_id.max_accrued_points -= coupon_point.max_accrued_points
            coupon_point.max_accrued_points = 0.0

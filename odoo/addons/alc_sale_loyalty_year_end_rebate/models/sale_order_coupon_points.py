# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrderCouponPoints(models.Model):
    _inherit = "sale.order.coupon.points"

    order_id = fields.Many2one("sale.order", index="btree")
    coupon_id = fields.Many2one("loyalty.card", index="btree")

    max_points = fields.Float(default=0.0)

    def _partition_by_order_id_and_program_id(self, program_type="year_end_rebate"):
        coupon_points_by_order_and_program = {}
        program_ids = set()
        order_ids = set()
        for coupon_points in self:
            loyalty_card = coupon_points.coupon_id
            if not loyalty_card.program_type == program_type:
                continue
            key = (coupon_points.order_id.id, loyalty_card.program_id.id)
            coupon_points_by_order_and_program[key] = coupon_points
            program_ids.add(loyalty_card.program_id.id)
            order_ids.add(coupon_points.order_id.id)
        return coupon_points_by_order_and_program, program_ids, order_ids

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        res._refresh_max_points()
        return res

    def write(self, vals):
        res = super().write(vals)
        if "points" in vals:
            self._refresh_max_points()
        return res

    def unlink(self):
        self._remove_coupon_max_points()
        return super().unlink()

    def _remove_coupon_max_points(self):
        for coupon_point in self:
            coupon_point.coupon_id.max_points -= coupon_point.max_points

    def _refresh_max_points(self):
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
                    sum(sol.price_subtotal * COALESCE(NULLIF(lr.reward_point_max_amount, 0), lr.reward_point_amount))
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
            for order_id, program_id, points in self.env.cr.fetchall():
                coupon_point = coupon_points_by_order_and_program.pop(
                    (order_id, program_id)
                )
                old_value = coupon_point.max_points
                new_value = points or 0.0
                if old_value != new_value:
                    coupon_point.coupon_id.max_points -= old_value
                    coupon_point.coupon_id.max_points += new_value
                coupon_point.max_points = new_value
        # Reset the remaining coupon points since they are no values for them
        for coupon_point in coupon_points_by_order_and_program.values():
            coupon_point.coupon_id.max_points -= coupon_point.max_points
            coupon_point.max_points = 0.0

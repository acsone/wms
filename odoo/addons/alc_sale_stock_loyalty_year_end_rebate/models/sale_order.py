# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.tools import float_compare, str2bool


class SaleOrder(models.Model):
    _inherit = "sale.order"

    rebate_accrued_total_amount = fields.Float(
        help="The amount total of rebate accrued for the current partner.",
        compute="_compute_rebate_amounts",
        default=0.0,
    )
    rebate_accrued_total_max_amount = fields.Float(
        help="The amount total max of rebate accrued for the current partner.",
        compute="_compute_rebate_amounts",
        default=0.0,
    )

    rebate_accrued_amount = fields.Float(
        help="The amount of rebate accrued for the current partner.",
        compute="_compute_rebate_amounts",
        default=0.0,
    )

    rebate_accrued_max_amount = fields.Float(
        help="The max amount of rebate accrued for the current partner.",
        compute="_compute_rebate_amounts",
        default=0.0,
    )

    rebate_potential_amount = fields.Float(
        help="The amount of rebate potential for the current order "
        "if all products are delivered.",
        compute="_compute_rebate_amounts",
        default=0.0,
    )

    rebate_potential_max_amount = fields.Float(
        help="The max amount of rebate potential for the current order "
        "if all products are delivered.",
        compute="_compute_rebate_amounts",
        default=0.0,
    )

    is_rebate_accrued_total_max_amount_visible = fields.Boolean(
        compute="_compute_is_rebate_accrued_total_max_amount_visible"
    )

    is_rebate_accrued_max_amount_visible = fields.Boolean(
        compute="_compute_is_rebate_accrued_max_amount_visible"
    )

    is_rebate_potential_max_amount_visible = fields.Boolean(
        compute="_compute_is_rebate_max_amount_visible"
    )

    rfa_program_id = fields.Many2one(
        "loyalty.program",
        help="The loyalty program used to calculate the rebate.",
        compute="_compute_rfa_program_id",
    )

    @api.depends("rebate_accrued_total_max_amount", "rebate_accrued_total_amount")
    def _compute_is_rebate_accrued_total_max_amount_visible(self):
        for order in self:
            order.is_rebate_accrued_total_max_amount_visible = (
                float_compare(
                    order.rebate_accrued_total_max_amount,
                    order.rebate_accrued_total_amount,
                    2,
                )
                > 0
            )

    @api.depends("rebate_accrued_max_amount", "rebate_accrued_amount")
    def _compute_is_rebate_accrued_max_amount_visible(self):
        for order in self:
            order.is_rebate_accrued_max_amount_visible = (
                float_compare(
                    order.rebate_accrued_max_amount, order.rebate_accrued_amount, 2
                )
                > 0
            )

    @api.depends("rebate_potential_max_amount", "rebate_potential_amount")
    def _compute_is_rebate_max_amount_visible(self):
        for order in self:
            order.is_rebate_potential_max_amount_visible = (
                float_compare(
                    order.rebate_potential_max_amount, order.rebate_potential_amount, 2
                )
                > 0
            )

    @api.depends("coupon_point_ids")
    def _compute_rebate_amounts(self):
        for order in self:
            accrued_total_points = 0.0
            accrued_points = 0.0
            potential_points = 0.0
            accrued_total_max_points = 0.0
            accrued_max_points = 0.0
            potential_max_points = 0.0
            rebate_coupon_points = order.coupon_point_ids.filtered(
                lambda cp: cp.coupon_id.program_type == "year_end_rebate"
            )
            if rebate_coupon_points:
                accrued_total_points = sum(
                    rebate_coupon_points.coupon_id.mapped("accrued_points")
                )
                potential_points = sum(rebate_coupon_points.mapped("points"))
                accrued_points = sum(rebate_coupon_points.mapped("accrued_points"))
                accrued_total_max_points = sum(
                    rebate_coupon_points.coupon_id.mapped("max_accrued_points")
                )
                potential_max_points = sum(rebate_coupon_points.mapped("max_points"))
                accrued_max_points = sum(
                    rebate_coupon_points.mapped("max_accrued_points")
                )
            order.rebate_accrued_total_amount = accrued_total_points
            order.rebate_potential_amount = potential_points
            order.rebate_accrued_amount = accrued_points
            order.rebate_accrued_total_max_amount = accrued_total_max_points
            order.rebate_potential_max_amount = potential_max_points
            order.rebate_accrued_max_amount = accrued_max_points

    def _display_rebate_on_report(self):
        display_rebate_on_sale_order_report = str2bool(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param(
                "alc_sale_stock_loyalty_year_end_rebate.display_rebate_on_sale_order_report"
            )
        )
        return display_rebate_on_sale_order_report and (
            self.rebate_potential_amount > 0.0 or self.rebate_accrued_total_amount > 0.0
        )

    @api.depends("coupon_point_ids")
    def _compute_rfa_program_id(self):
        for order in self:
            order.rfa_program_id = fields.first(
                order.coupon_point_ids.filtered(
                    lambda cp: cp.coupon_id.program_type == "year_end_rebate"
                )
            ).coupon_id.program_id

    def _update_programs_and_rewards(self):
        res = super()._update_programs_and_rewards()
        self.coupon_point_ids._refresh_accrued_points()
        return res

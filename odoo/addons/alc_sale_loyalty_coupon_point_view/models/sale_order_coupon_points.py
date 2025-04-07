# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleOrderCouponPoints(models.Model):

    _inherit = "sale.order.coupon.points"

    date_order = fields.Datetime(
        related="order_id.date_order",
        store=True,
    )
    coupon_partner_id = fields.Many2one(
        related="coupon_id.partner_id",
        string="Beneficiary",
        store=True,
        ondelete="cascade",
    )
    order_partner_id = fields.Many2one(
        related="order_id.partner_id",
        string="Customer",
        store=True,
        ondelete="cascade",
    )

    program_id = fields.Many2one(
        related="coupon_id.program_id",
        string="Loyalty Program",
        store=True,
        ondelete="cascade",
    )

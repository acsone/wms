# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleOrderCouponPoints(models.Model):
    _inherit = "sale.order.coupon.points"

    order_id = fields.Many2one("sale.order", index="btree")
    coupon_id = fields.Many2one("loyalty.card", index="btree")

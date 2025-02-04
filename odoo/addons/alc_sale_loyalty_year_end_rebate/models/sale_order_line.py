# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleOrderLine(models.Model):

    _inherit = "sale.order.line"

    coupon_id = fields.Many2one("loyalty.card", index="btree_not_null")
    reward_id = fields.Many2one("loyalty.reward", index="btree_not_null")

# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class LoyaltyCard(models.Model):

    _inherit = "loyalty.card"

    accrued_points = fields.Float(
        help="The amount of points that will be converted into a rebate "
        "based on delivered quantities.",
        default=0.0,
    )

    max_accrued_points = fields.Float(
        help="The maximum amount of points that can be earned with the card "
        "if all the rules have overperformed.",
        default=0.0,
    )

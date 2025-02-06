# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class LoyaltyCard(models.Model):

    _inherit = "loyalty.card"

    program_type = fields.Selection(related="program_id.program_type", store=True)

    accrued_points = fields.Float(
        string="Accrued Points",
        help="The amount of points that will be converted into a rebate "
        "based on delivered quantities.",
        default=0.0,
    )

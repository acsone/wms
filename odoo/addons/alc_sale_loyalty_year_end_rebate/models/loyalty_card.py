# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class LoyaltyCard(models.Model):

    _inherit = "loyalty.card"

    program_type = fields.Selection(related="program_id.program_type", store=True)

    max_points = fields.Float(
        string="Max Points",
        help="The maximum amount of points earned with the card if all the rules "
        "have overperformed.",
        default=0.0,
    )

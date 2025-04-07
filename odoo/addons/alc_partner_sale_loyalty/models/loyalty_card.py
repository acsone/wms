# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class LoyaltyCard(models.Model):

    _inherit = "loyalty.card"

    beneficiary_partner_type = fields.Selection(
        related="program_id.beneficiary_partner_type", store=True
    )

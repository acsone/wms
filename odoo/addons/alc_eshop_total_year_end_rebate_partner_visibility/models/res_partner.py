# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartner(models.Model):

    _inherit = "res.partner"

    is_total_year_end_rebate_visible = fields.Boolean(
        string="Can See Total Year End Rebate",
        help="If checked, the partner can see the total of "
        "cumulated year end rebate from the website.",
        default=True,
    )

    def _allows_see_total_year_end_rebate(self):
        """
        Check if the partner can see the total of cumulated year end rebate.

        from the website.
        """
        return (
            self.is_total_year_end_rebate_visible
            and self.is_valid_vet_efficiency_member
        )

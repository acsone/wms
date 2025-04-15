# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class LoyaltyProgram(models.Model):
    _inherit = "loyalty.program"

    def _compute_all_restricted_partner_ids(self):
        original_partner_ids = set(self.all_restricted_partner_ids.ids)
        res = super()._compute_all_restricted_partner_ids()
        updated_partner_ids = set(self.all_restricted_partner_ids.ids)
        if original_partner_ids != updated_partner_ids:
            diff_partner_ids = original_partner_ids ^ updated_partner_ids
            self.env["res.partner"].browse(
                list(diff_partner_ids)
            ).keycloak_user_ids.check_update_on_keycloak_backend(
                {"restricted_loyalty_program_ids": None}
            )
        return res

# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class LoyaltyRule(models.Model):
    _inherit = "loyalty.rule"

    @api.model_create_multi
    def create(self, vals_list):
        """Override create method to set the sequence of the loyalty rule."""
        res = super().create(vals_list)
        res.mapped("program_id")._se_mark_to_update()
        return res

    def write(self, vals):
        """Override write method to set the sequence of the loyalty rule."""
        res = super().write(vals)
        self.mapped("program_id")._se_mark_to_update()
        return res

    def unlink(self):
        self.mapped("program_id")._se_mark_to_update()
        return super().unlink()

# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class LoyaltyRule(models.Model):
    _name = "loyalty.rule"
    _inherit = ["loyalty.rule", "se.product.update.mixin"]

    def get_products(self):
        active_programs = self.mapped("program_id").filtered(
            lambda p: p._is_program_still_valid()
        )
        return self.filtered(lambda r, ap=active_programs: r.program_id in ap).mapped(
            "product_ids"
        )

    def needs_product_update(self, vals):
        return "sequence" in vals or "product_ids" in vals

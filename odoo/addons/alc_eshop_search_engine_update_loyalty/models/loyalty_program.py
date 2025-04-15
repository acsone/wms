# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class LoyaltyProgam(models.Model):
    _name = "loyalty.program"
    _inherit = ["loyalty.program", "se.product.update.mixin"]

    def _is_program_still_valid(self):
        """Check if the program is still valid based on the date range."""
        self.ensure_one()
        return self.active and (not self.date_to or self.date_to >= fields.Date.today())

    def get_products(self):
        return self.mapped("rule_ids.product_ids")

    def needs_product_update(self, vals):
        return "active" in vals or "date_to" in vals or "date_from" in vals

# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import date

from odoo import Command, fields, models


class LoyaltyProgram(models.Model):
    _name = "loyalty.program"
    _inherit = ["loyalty.program", "alc.eshop.temporal.info.mixin"]

    date_start = fields.Date(compute="_compute_date_start", store=True, precompute=True)
    date_end = fields.Date(compute="_compute_date_end", store=True, precompute=True)

    def _compute_date_start(self):
        """Compute the start date of the loyalty program."""
        for record in self:
            record.date_start = record.date_from if record.date_from else date.today()

    def _compute_date_end(self):
        """Compute the end date of the loyalty program."""
        for record in self:
            record.date_end = record.date_to if record.date_to else date.max

    def _compute_se_index(self):
        model = self.env.ref("loyalty.model_loyalty_program")
        indexes = self.env["se.index"].search([("model_id", "=", model.id)])
        self.update({"se_index_ids": [Command.set(indexes.ids)]})

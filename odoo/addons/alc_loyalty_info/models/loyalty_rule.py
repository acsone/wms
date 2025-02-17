# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class LoyaltyRule(models.Model):

    _inherit = "loyalty.rule"
    _order = "sequence, name"

    sequence = fields.Integer(default=-1, required=True)
    name = fields.Char(
        translate=True,
    )

    def name_get(self):
        result = []
        self_with_name = self.filtered("name")
        for record in self_with_name:
            result.append((record.id, record.name))
        result.extend(super(LoyaltyRule, self - self_with_name).name_get())
        return result

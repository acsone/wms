# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command, _, api, fields, models


class LoyaltyProgram(models.Model):

    _inherit = "loyalty.program"

    program_type = fields.Selection(
        selection_add=[("year_end_rebate", "Year-end Rebate")],
        ondelete={
            "year_end_rebate": "cascade",
        },
    )

    @api.model
    def _program_items_name(self):
        res = super()._program_items_name()
        res["year_end_rebate"] = _("Year-end Rebate")
        return res

    @api.model
    def _program_type_default_values(self):
        res = super()._program_type_default_values()
        res["year_end_rebate"] = {
            "applies_on": "both",
            "trigger": "auto",
            "portal_visible": True,
            "portal_point_name": _("Year-end Rebate"),
            "rule_ids": [
                Command.clear(),
                Command.create(
                    {
                        "reward_point_mode": "money",
                    }
                ),
            ],
            "reward_ids": [
                Command.clear(),
                Command.create(
                    {
                        "discount": 0,
                        "required_points": 1,
                        "reward_type": "rebate",
                    }
                ),
            ],
            "communication_plan_ids": [Command.clear()],
        }

        return res

    def _compute_is_nominative(self):
        res = super()._compute_is_nominative()
        for program in self:
            if program.program_type == "year_end_rebate":
                program.is_nominative = True
        return res

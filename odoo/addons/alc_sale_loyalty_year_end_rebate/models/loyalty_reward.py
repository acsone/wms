# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, fields, models


class LoyaltyReward(models.Model):

    _inherit = "loyalty.reward"

    reward_type = fields.Selection(
        selection_add=[("rebate", "Rebate")],
        ondelete={
            "rebate": "cascade",
        },
    )

    def _compute_description(self):
        res = super()._compute_description()
        for reward in self:
            if reward.reward_type == "rebate":
                reward.description = _("Rebate of cumulated amount")
        return res

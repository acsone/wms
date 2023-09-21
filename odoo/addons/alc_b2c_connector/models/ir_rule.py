# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api

from odoo.addons.fastapi.models.ir_rule import IrRule as IrRuleBase


class IrRule(IrRuleBase):
    @api.model
    def _eval_context(self):
        ctx = super()._eval_context()
        # If 'alc_b2c_client_id' is not found in the context,
        # we set it to -1 (an impossible ID) to prevent rules from crashing
        # due to the missing key.
        ctx["alc_b2c_client_id"] = self.env.context.get("alc_b2c_client_id", -1)
        return ctx

    def _compute_domain_keys(self):
        return super()._compute_domain_keys() + ["alc_b2c_client_id"]

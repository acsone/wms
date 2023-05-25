# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api

from odoo.addons.fastapi.models.ir_rule import IrRule as IrRuleBase


class IrRule(IrRuleBase):
    @api.model
    def _eval_context(self):
        ctx = super()._eval_context()
        if "alc_b2c_client_id" in self.env.context:
            ctx["alc_b2c_client_id"] = self.env.context["alc_b2c_client_id"]
        return ctx

    def _compute_domain_keys(self):
        return super()._compute_domain_keys() + ["alc_b2c_client_id"]

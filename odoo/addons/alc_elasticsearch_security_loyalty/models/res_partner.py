# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api

from odoo.addons.base.models.res_partner import Partner


class ResPartner(Partner):
    @api.depends(
        "restricted_loyalty_program_ids",
    )
    def _compute_elasticsearch_role(self):
        res = super()._compute_elasticsearch_role()
        self.env["loyalty.program"].flush_model(["all_restricted_partner_ids"])
        for partner in self:
            roles = partner.elasticsearch_role
            loyalty_program_roles = ",".join(
                partner.restricted_loyalty_program_ids.mapped(
                    lambda v: v._get_role_name()
                )
            )
            if loyalty_program_roles:
                roles = ",".join((partner.elasticsearch_role, loyalty_program_roles))
                partner.elasticsearch_role = roles
        return res

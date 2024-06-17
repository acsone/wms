# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api

from odoo.addons.base.models.res_partner import Partner


class ResPartner(Partner):
    @api.depends(
        "partner_type",
        "supplier_promotion_sale_allowed",
        "property_product_pricelist",
        "discount_pricelist_ids",
        "veterinary_group_ids",
        "date_start_contract_alcyonnaire",
        "date_end_contract_alcyonnaire",
    )
    def _compute_elasticsearch_role(self):
        res = super()._compute_elasticsearch_role()
        for partner in self:
            roles = partner.elasticsearch_role
            vt_roles = ",".join(
                partner.veterinary_group_ids.mapped(lambda v: v._get_role_name())
            )
            if vt_roles:
                roles = ",".join((partner.elasticsearch_role, vt_roles))
            role_a = "non_alcyonnaire"
            if partner.is_alcyonnaire:
                role_a = "is_alcyonnaire"
            if partner.is_alcyonnaire_under_contract:
                role_a = "is_alcyonnaire_under_contract"
            roles = ",".join((roles, role_a))
            partner.elasticsearch_role = roles
        return res

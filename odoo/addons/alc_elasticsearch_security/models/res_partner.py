# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields

from odoo.addons.base.models.res_partner import Partner


class ResPartner(Partner):

    elasticsearch_role = fields.Char(compute="_compute_elasticsearch_role", store=False)

    def _get_pricelist_roles(self):
        roles = self.discount_pricelist_ids.mapped("role_name")
        return roles + [self.property_product_pricelist.role_name]

    def _get_elasticearch_roles(self):
        self.ensure_one()
        partner_type = self.partner_type
        roles = {partner_type} | set(self._get_pricelist_roles())
        roles |= {self.supplier_promotion_sale_allowed and "supplier_promotion"}
        if partner_type != "supplier":  # supplier can see prices...
            roles.add("guest")
        return {r for r in roles if r}

    @api.depends(
        "partner_type",
        "supplier_promotion_sale_allowed",
        "property_product_pricelist",
        "discount_pricelist_ids",
    )
    def _compute_elasticsearch_role(self):
        for partner in self:
            partner.elasticsearch_role = ",".join(partner._get_elasticearch_roles())

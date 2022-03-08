# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResPartner(models.Model):

    _inherit = "res.partner"

    elasticsearch_role = fields.Char(compute="_compute_elasticsearch_role", store=False)
    pricelist_role = fields.Char(compute="_compute_pricelist_role", store=False)
    discount_pricelist_role = fields.Char(
        compute="_compute_pricelist_role", store=False
    )

    @api.depends("property_product_pricelist", "discount_pricelist_id")
    def _compute_pricelist_role(self):
        for partner in self:
            partner.pricelist_role = partner.property_product_pricelist.role_name
            partner.discount_pricelist_role = partner.discount_pricelist_id.role_name

    def _get_elasticearch_roles(self):
        self.ensure_one()
        partner_type = self.partner_type
        roles = {
            partner_type,
            self.pricelist_role,
            self.discount_pricelist_role,
            self.supplier_promotion_sale_allowed and "supplier_promotion",
        }
        if partner_type != "supplier":  # supplier can see prices...
            roles.add("guest")
        return {r for r in roles if r}

    @api.depends("partner_type", "pricelist_role", "supplier_promotion_sale_allowed")
    def _compute_elasticsearch_role(self):
        # depends on property_product_pricelist.name, but this isn't stored
        roles = {
            p: ",".join(p._get_elasticearch_roles())
            for p in self.with_context(lang=False)
        }
        for partner in self:
            partner.elasticsearch_role = roles[partner]

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

    @api.depends("partner_type", "pricelist_role", "supplier_promotion_sale_allowed")
    def _compute_elasticsearch_role(self):
        # depends on property_product_pricelist.name, but this isn't stored
        roles = {
            p: ",".join(
                {
                    e
                    for e in {
                        "guest",
                        p.partner_type,
                        p.pricelist_role,
                        p.discount_pricelist_role,
                        p.supplier_promotion_sale_allowed and "supplier_promotion",
                    }
                    if e
                }
            )
            for p in self.with_context(lang=False)
        }
        for partner in self:
            partner.elasticsearch_role = roles[partner]

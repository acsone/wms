# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResPartner(models.Model):

    _inherit = "res.partner"

    elasticsearch_role = fields.Char(compute="_compute_elasticsearch_role", store=False)

    @api.depends("partner_type")
    def _compute_elasticsearch_role(self):
        # depends on property_product_pricelist.name, but this isn't stored
        roles = {
            p: ",".join({"guest", p.partner_type, p.property_product_pricelist.name})
            for p in self.with_context(lang=False)
        }
        for partner in self:
            partner.elasticsearch_role = roles[partner]

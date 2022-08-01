# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, models


class ProductPricelist(models.Model):

    _inherit = "product.pricelist"

    @api.model
    def create(self, vals):
        res = super(ProductPricelist, self).create(vals)
        res.delay_create_or_update_pricelist_role()
        return res

    def unlink(self):
        domain_roles = [("pricelist_id", "in", self.ids)]
        self.env["elasticsearch.role"].search(domain_roles).delay_delete_role()
        return super(ProductPricelist, self).unlink()

    def delay_create_or_update_pricelist_role(self):
        backends = self.env["se.backend.elasticsearch"].search([])
        for backend in backends:
            for pl in self:
                desc = _("Create Pricelist Role on ElasticSearch: %s") % pl.name
                backend.with_delay(description=desc).create_or_update_pricelist_role(pl)

    def write(self, vals):
        if "name" in vals:
            self.delay_create_or_update_pricelist_role()
        return super(ProductPricelist, self).write(vals)

# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, models


class ProductPricelist(models.Model):

    _inherit = "product.pricelist"

    @api.model
    def create(self, vals):
        res = super(ProductPricelist, self).create(vals)
        backends = self.env["se.backend.elasticsearch"].search([])
        for backend in backends:
            desc = _("Create Pricelist on ElasticSearch: %s") % res.name
            backend.with_delay(description=desc).create_or_update_pricelist_role(res)
        return res

# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, tools
from odoo.osv.expression import AND


class ProductProduct(models.Model):
    _inherit = "product.product"

    price_cache = fields.Serialized(readonly=True)

    @api.model
    @tools.ormcache()
    def get_price_cache_products_domain(self):
        res = super(ProductProduct, self).get_price_cache_products_domain()
        assortment = self.env.ref("alc_eshop.shopinvader_assortment_store")
        domain_assortment = assortment._get_eval_domain()
        return AND([res, domain_assortment])

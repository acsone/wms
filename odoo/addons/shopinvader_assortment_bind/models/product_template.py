# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class ProductTemplate(models.Model):

    _inherit = "product.template"

    def shopinvader_assortment_binding(self, backend_domain=None):
        products = self.mapped("product_variant_ids")
        products.shopinvader_assortment_binding(backend_domain=backend_domain)

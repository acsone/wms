# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class ProductProduct(models.Model):

    _inherit = "product.product"

    def shopinvader_assortment_binding(self, backend_domain=None):
        self.env["shopinvader.backend"].autobind_product_from_assortment(
            domain=backend_domain, domain_product=[("id", "in", self.ids)],
        )

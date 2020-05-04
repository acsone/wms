# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import models


class ProductProduct(models.Model):
    _name = "product.product"
    _inherit = ["product.product", "esb.exportable"]

    def _is_product_fit_to_export(self):
        """Check if a product is valid to be exported.

        Only stockable product that are ok for sale are exported.
        """
        return self.type == "product" and self.sale_ok

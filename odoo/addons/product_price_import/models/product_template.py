# -*- coding: utf-8 -*-
# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class ProductTemplate(models.Model):

    _inherit = "product.template"

    @api.model
    def _get_default_supplierinfo(self, products):
        """
        Return the default supplier_info by product_tmpl_id, IOW the one
        without start and end date
        """
        si = self.env["product.supplierinfo"].search(
            [
                ("product_tmpl_id", "in", products.ids),
                ("date_start", "=", False),
                ("date_end", "=", False),
            ]
        )
        return {i.product_tmpl_id: i for i in si}

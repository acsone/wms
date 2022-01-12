# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class StockLocation(models.Model):

    _inherit = "stock.location"

    def _get_product_putaway(self, product):
        stock_bin_ids = product.product_tmpl_id.stock_bin_ids
        lbin = stock_bin_ids.filtered(
            lambda b, location_id=self.id: b.location_id.id == location_id
            and b.is_bin_location_active
        )
        if lbin:
            return lbin[0].bin_location_id
        return super(StockLocation, self)._get_product_putaway(product)

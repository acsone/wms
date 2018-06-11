# -*- coding: utf-8 -*-
# Copyright 2018 Sylvain VAN HOOF (Okia SPRL)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class StockScrap(models.Model):
    _inherit = 'stock.scrap'

    @api.onchange('product_id')
    def onchange_product_id(self):
        self.ensure_one()

        result = super(StockScrap, self).onchange_product_id()

        bins = self.product_id.stock_bin_ids
        if bins:
            self.location_id = bins[0].bin_location_id.id
        else:
            self.location_id = self._get_default_location_id()

        return result

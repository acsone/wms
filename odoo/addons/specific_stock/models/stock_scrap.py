# -*- coding: utf-8 -*-
# Copyright 2018 Sylvain VAN HOOF (Okia SPRL)
# Copyright 2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockScrap(models.Model):
    _inherit = "stock.scrap"

    def _get_default_scrap_location_id(self):
        # Set destination location to quality control
        try:
            return self.env.ref("__setup__.stock_location_scrap_quality").id
        except ValueError:
            return super(StockScrap, self)._get_default_scrap_location_id()

    scrap_location_id = fields.Many2one(default=_get_default_scrap_location_id)

    @api.onchange("product_id")
    def onchange_product_id(self):
        self.ensure_one()

        result = super(StockScrap, self).onchange_product_id()

        bins = self.product_id.stock_bin_ids
        if bins:
            self.location_id = bins[0].bin_location_id.id
        else:
            self.location_id = self._get_default_location_id()

        return result

# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api

from odoo.addons.alc_price_cache.models.product_pricelist_item import (
    ProductPricelistItem as ProductPricelistItemBase,
)


class ProductPricelistItem(ProductPricelistItemBase):
    @api.model
    def load(self, fields, data):
        """Batch price re-computation that happen with consecutive writes."""
        self_no_update = self.with_context(no_update_price_cache=True)
        res = super(ProductPricelistItem, self_no_update).load(fields, data)
        pricelists = self.browse(res["ids"]).mapped("pricelist_id")
        pricelists._delay_update_price_cache()
        return res

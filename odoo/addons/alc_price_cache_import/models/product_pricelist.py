# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api

from odoo.addons.alc_price_cache.models.product_pricelist import (
    ProductPricelist as ProductPricelistBase,
)


class ProductPricelist(ProductPricelistBase):
    @api.model
    def load(self, fields, data):
        """Batch price re-computation that happen with consecutive writes."""
        self_no_update = self.with_context(no_update_price_cache=True)
        res = super(ProductPricelist, self_no_update).load(fields, data)
        self.browse(res["ids"])._delay_update_price_cache()
        return res

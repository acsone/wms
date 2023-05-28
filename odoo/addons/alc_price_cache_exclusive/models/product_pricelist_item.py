# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.addons.alc_price_cache.models.product_pricelist_item import (
    ProductPricelistItem as ProductPricelistItemBase,
)


class ProductPricelistItem(ProductPricelistItemBase):
    def _cache_discount(self, product):
        res = super()._cache_discount(product)
        if res:
            res["exclusive"] = self.exclusive
        return res

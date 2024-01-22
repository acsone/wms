# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader_search_engine_product_stock.models.product_product import (
    ProductProduct as ProductProductBase,
)


class ProductProduct(ProductProductBase):
    def synchronize_all_binding_stock_level(self, company_id=None):
        res = super().synchronize_all_binding_stock_level(company_id=company_id)
        products = self
        if company_id:
            products = self.with_company(company_id)
        all_bindinds = products.mapped("se_binding_ids")
        indexes = all_bindinds.mapped("index_id")
        for index in indexes:
            for product in products.with_context(index_id=index.id)._filter_by_index():
                binding = product.sudo().se_binding_ids.filtered(
                    lambda b, i=index: b.index_id == i
                )
                if (
                    not binding.data
                    or binding.state == "to_recompute"
                    or binding.data.get("best_before_date")
                    == (
                        product.best_before_date.isoformat()
                        if product.best_before_date
                        else None
                    )
                ):
                    continue
                # the stock data are the same but the best before date has changed
                binding.state = "to_recompute"
        return res

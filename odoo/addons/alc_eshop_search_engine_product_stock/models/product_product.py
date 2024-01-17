# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api

from odoo.addons.shopinvader_search_engine_product_stock.models import product_product


class ProductProduct(product_product.ProductProduct):
    @api.model
    def cron_sync_stock_level(self, batch_size=100):
        """Sync stock level for all products."""
        assortment = self.env.ref(
            "alc_eshop_product_domain.shopinvader_assortment_store"
        )
        domain = assortment._get_eval_domain()
        products = self.search(domain)
        count = len(products)
        done = 0
        for batch in products.batch(batch_size):
            batch_size = len(batch)
            batch.with_delay(
                description=_(
                    "Batch synchronize stock level for products from %(_from)s to %(to)s on %(on)s",
                    _from=done,
                    to=done + batch_size,
                    on=count,
                )
            ).synchronize_all_binding_stock_level()
            done += batch_size

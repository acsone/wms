# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .common import TestPriceDomain


class TestPriceDomainFlow(TestPriceDomain):
    def test_get_domain(self):
        # This test will break if the shop assortment is modified
        domain = self.env["product.product"].get_price_cache_products_domain()

        self.assertEqual(domain, [("web_published", "=", True)])

    def test_get_products(self):
        """Check that we get products from the assortment, and no others.
           This test will break if the shop assortment is modified.
        """
        self.assortment.whitelist_product_ids = self.product_whitelisted
        self.assortment.blacklist_product_ids = self.product_blacklisted

        products = self.env["product.product"].get_price_cache_products()

        self.assertTrue(self.product_1 in products)
        self.assertTrue(self.product_whitelisted in products)
        self.assertFalse(self.product_2 in products)
        self.assertFalse(self.product_blacklisted in products)
        # if filtered_domain is available, then we have
        # products.filtered_domain(domain) == products

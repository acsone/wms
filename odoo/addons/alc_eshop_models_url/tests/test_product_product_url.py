# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from .common import TestUrlCase


class TestCategoryUrl(TestUrlCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env["product.template"].create({"name": "product 1"})

    def test_00(self):
        """Without default code."""
        self.product.default_code = False
        self.product._update_url_key(lang="en_US")
        self.assertUrlForLang(self.product, "en_US", "p/product-1")

    def test_01(self):
        """With default code."""
        self.product.default_code = "default_code"
        self.product._update_url_key(lang="en_US")
        self.assertUrlForLang(self.product, "en_US", "p/product-1-default-code")

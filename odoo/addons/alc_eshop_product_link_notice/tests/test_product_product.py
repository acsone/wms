# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase

from odoo.addons.extendable.tests.common import ExtendableMixin
from odoo.addons.shopinvader_product.schemas.product import ProductProduct


class TestProductSchema(TransactionCase, ExtendableMixin):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.init_extendable_registry()
        cls.addClassCleanup(cls.reset_extendable_registry)

        cls.product = cls.env["product.product"].create(
            {"name": "test product", "tracking": "lot", "type": "product"}
        )

    def test_00(self):
        product = ProductProduct.from_product_product(self.product)
        self.assertIsNone(product.link_info)
        self.product.link_info = "link_info"
        product = ProductProduct.from_product_product(self.product)
        self.assertEqual(product.link_info, "link_info")

    def test_01(self):
        product = ProductProduct.from_product_product(self.product)
        self.assertIsNone(product.link_notice)
        self.product.link_notice = "link_notice"
        product = ProductProduct.from_product_product(self.product)
        self.assertEqual(product.link_notice, "link_notice")

    def test_02(self):
        product = ProductProduct.from_product_product(self.product)
        self.assertIsNone(product.link_video)
        self.product.link_video = "link_video"
        product = ProductProduct.from_product_product(self.product)
        self.assertEqual(product.link_video, "link_video")

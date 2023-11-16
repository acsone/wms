# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase

from odoo.addons.extendable.tests.common import ExtendableMixin

from ..schemas import ProductProduct


class TestProductExpiryInSchema(TransactionCase, ExtendableMixin):
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
        self.assertFalse(product.promo_bag)
        self.product.promo_bag = True
        product = ProductProduct.from_product_product(self.product)
        self.assertTrue(product.promo_bag)

    def test_01(self):
        product = ProductProduct.from_product_product(self.product)
        self.assertFalse(product.sterile)
        self.product.sterile = True
        product = ProductProduct.from_product_product(self.product)
        self.assertTrue(product.sterile)

    def test_02(self):
        product = ProductProduct.from_product_product(self.product)
        self.assertFalse(product.fabric)
        self.product.fabric = True
        product = ProductProduct.from_product_product(self.product)
        self.assertTrue(product.fabric)

    def test_03(self):
        product = ProductProduct.from_product_product(self.product)
        self.assertIsNone(product.description_shop_short)
        self.product.description_shop_short = "description_shop_short"
        product = ProductProduct.from_product_product(self.product)
        self.assertEqual(product.description_shop_short, "description_shop_short")

    def test_04(self):
        product = ProductProduct.from_product_product(self.product)
        self.assertIsNone(product.description_shop_long)
        self.product.description_shop_long = "description_shop_long"
        product = ProductProduct.from_product_product(self.product)
        self.assertEqual(product.description_shop_long, "description_shop_long")

    def test_05(self):
        product = ProductProduct.from_product_product(self.product)
        self.assertIsNone(product.class_amcra)
        self.product.class_amcra = "yellow"
        product = ProductProduct.from_product_product(self.product)
        self.assertEqual(product.class_amcra, "yellow")

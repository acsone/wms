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
        cls.manufacturer = cls.env["res.partner"].create({"name": "manufacturer"})

    def test_00(self):
        product = ProductProduct.from_product_product(self.product)
        self.assertIsNone(product.barcode)
        self.product.barcode = "barcode"
        product = ProductProduct.from_product_product(self.product)
        self.assertEqual(product.barcode, "barcode")

    def test_01(self):
        product = ProductProduct.from_product_product(self.product)
        self.assertIsNone(product.manufacturer)
        self.product.manufacturer_id = self.manufacturer.id
        product = ProductProduct.from_product_product(self.product)
        self.assertEqual(product.manufacturer.name, self.manufacturer.name)
        self.assertEqual(product.manufacturer.id, self.manufacturer.id)

# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase

from odoo.addons.extendable.tests.common import ExtendableMixin
from odoo.addons.shopinvader_product.schemas.product import ProductProduct


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
        self.assertEqual(product.indicated_price, 0.0)
        self.product.indicated_price = 15.2
        product = ProductProduct.from_product_product(self.product)
        self.assertAlmostEqual(product.indicated_price, 15.2, 1)

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

        cls.product = cls.env["product.product"].create({"name": "test product"})
        cls.product.taxes_id = False
        cls.taxes = cls.tax = cls.env["account.tax"].create(
            [
                {"name": "10%", "amount_type": "percent", "amount": "10"},
                {"name": "15%", "amount_type": "percent", "amount": "15"},
            ]
        )

    def test_00(self):
        product = ProductProduct.from_product_product(self.product)
        self.assertEqual(product.taxes_id, [])
        self.product.taxes_id = self.taxes
        product = ProductProduct.from_product_product(self.product)
        self.assertSetEqual(set(product.taxes_id), {"10%", "15%"})

    def test_01(self):
        product = ProductProduct.from_product_product(self.product)
        self.assertIsNone(product.vat)
        tax = self.taxes[0]
        self.product.vat_id = tax
        product = ProductProduct.from_product_product(self.product)
        self.assertEqual(product.vat.id, tax.id)
        self.assertEqual(product.vat.name, tax.name)
        self.assertEqual(product.vat.amount, tax.amount)

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
        cls.supplier = cls.env["res.partner"].create({"name": "Supplier"})

    def test_00(self):
        product = ProductProduct.from_product_product(self.product)
        self.assertIsNone(product.vendor_product_code)
        self.assertIsNone(product.supplier_id)
        self.env["product.supplierinfo"].create(
            {
                "partner_id": self.supplier.id,
                "product_code": "product_code",
                "product_tmpl_id": self.product.product_tmpl_id.id,
            }
        )
        product = ProductProduct.from_product_product(self.product)
        self.assertEqual(product.vendor_product_code, "product_code")
        self.assertEqual(product.supplier_id, self.supplier.id)

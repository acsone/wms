# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase

from odoo.addons.extendable.tests.common import ExtendableMixin

from ..schemas import ProductProduct


class TestProductExpiryInSchema(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        ExtendableMixin.init_extendable_registry()

        @cls.addClassCleanup
        def cleanup():
            ExtendableMixin.reset_extendable_registry()

        cls.product = cls.env["product.product"].create(
            {"name": "test product", "tracking": "lot", "type": "product"}
        )
        cls.supplier = cls.env["res.partner"].create(
            {"name": "Supplier", "ref": "9001"}
        )
        cls.supplierinfo = cls.env["product.supplierinfo"].create(
            {"partner_id": cls.supplier.id, "product_code": "product_code"}
        )

    def test_00(self):
        product = ProductProduct.from_product_product(self.product)
        self.assertIsNone(product.vendor_product_code)
        self.assertIsNone(product.supplier_id)
        self.product.seller_ids = self.supplierinfo
        product = ProductProduct.from_product_product(self.product)
        self.assertEqual(product.vendor_product_code, "product_code")
        self.assertEqual(product.supplier_id, self.supplier.id)

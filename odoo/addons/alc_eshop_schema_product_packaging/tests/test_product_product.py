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
        cls.packaging_shrink = cls.env.ref(
            "alc_product_packaging.product_packaging_type_shrink_wrap"
        )
        cls.product_packaging = cls.env["product.packaging"].create(
            {"name": "p11_packaging", "qty": 30.0}
        )

    def test_00(self):
        product = ProductProduct.from_product_product(self.product)
        self.assertEqual(product.packaging_ids, [])
        self.assertEqual(product.unit_in_shrink_wrap, 0)
        self.product.packaging_ids = self.product_packaging
        self.product_packaging.packaging_level_id = self.packaging_shrink
        product = ProductProduct.from_product_product(self.product)
        self.assertEqual(product.packaging_ids, ["Fardelage (FAR)"])
        self.assertEqual(product.unit_in_shrink_wrap, 30)

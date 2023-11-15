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
        cls.packaging_shrink = cls.env.ref(
            "alc_product_packaging.product_packaging_type_shrink_wrap"
        )
        cls.product_packaging = cls.env["product.packaging"].create(
            {"name": "p11_packaging", "qty": 30.0}
        )
        cls.product.packaging_ids = cls.product_packaging

    def test_00(self):
        product = ProductProduct.from_product_product(self.product)
        self.assertEqual(product.unit_in_shrink_wrap, 0)
        self.product_packaging.packaging_level_id = self.packaging_shrink
        product = ProductProduct.from_product_product(self.product)
        self.assertEqual(product.unit_in_shrink_wrap, 30)

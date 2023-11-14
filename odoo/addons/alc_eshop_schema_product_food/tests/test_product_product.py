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
        cls.food_category = cls.env.ref(
            "alc_product_food.product_categ_ali", raise_if_not_found=False
        )

    def test_0(self):
        product = ProductProduct.from_product_product(self.product)
        self.assertFalse(product.is_food)
        self.product.categ_id = self.food_category
        product = ProductProduct.from_product_product(self.product)
        self.assertTrue(product.is_food)

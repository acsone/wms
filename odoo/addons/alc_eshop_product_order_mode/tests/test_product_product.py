# Copyright 2025 ACSONE SA/NV
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

        cls.shop_order_modes = [
            "direct_sale_only",
            "quotation_only",
            "direct_sale_or_quotation",
        ]
        cls.products = [
            cls.env["product.template"]
            .create(
                {
                    "name": f"Test product {i}",
                    "shop_order_mode": shop_order_mode,
                    "is_shop_order_mode_unabled_on_variant": True,
                }
            )
            .product_variant_id
            for i, shop_order_mode in enumerate(cls.shop_order_modes)
        ]

    def test_0(self):
        for product, shop_order_mode in zip(
            self.products, self.shop_order_modes, strict=True
        ):
            product_schema = ProductProduct.from_product_product(product)
            self.assertEqual(product_schema.shop_order_mode.value, shop_order_mode)

    def test_1(self):
        product = self.products[0]
        product_schema = ProductProduct.from_product_product(product)
        self.assertEqual(product_schema.shop_order_mode.value, "direct_sale_only")

        product.shop_order_mode = "quotation_only"
        product_schema = ProductProduct.from_product_product(product)
        self.assertEqual(product_schema.shop_order_mode.value, "quotation_only")

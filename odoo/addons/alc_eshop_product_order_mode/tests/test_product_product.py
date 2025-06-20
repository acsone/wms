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

        cls.order_modes = [
            "direct_sale_only",
            "quotation_only",
            "direct_sale_or_quotation",
        ]
        cls.products = [
            cls.env["product.template"]
            .create(
                {
                    "name": f"Test product {i}",
                    "shop_order_mode": order_mode,
                }
            )
            .product_variant_id
            for i, order_mode in enumerate(cls.order_modes)
        ]

    def test_0(self):
        for product, order_mode in zip(self.products, self.order_modes, strict=True):
            product_schema = ProductProduct.from_product_product(product)
            self.assertEqual(product_schema.order_mode.value, order_mode)

    def test_1(self):
        product = self.products[0]
        product_schema = ProductProduct.from_product_product(product)
        self.assertEqual(product_schema.order_mode.value, "direct_sale_only")

        product.product_tmpl_id.is_shop_order_mode_enabled_on_variant = True
        product.shop_order_mode = "quotation_only"
        product_schema = ProductProduct.from_product_product(product)
        self.assertEqual(product_schema.order_mode.value, "quotation_only")

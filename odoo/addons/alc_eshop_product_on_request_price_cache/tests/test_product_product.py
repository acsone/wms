# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from datetime import date, timedelta

from odoo import Command
from odoo.tests.common import TransactionCase

from odoo.addons.extendable.tests.common import ExtendableMixin
from odoo.addons.shopinvader_product.schemas.product import ProductProduct


class TestProductSchema(TransactionCase, ExtendableMixin):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.init_extendable_registry()
        cls.addClassCleanup(cls.reset_extendable_registry)

        cls.product = (
            cls.env["product.template"]
            .create(
                {"name": "test product", "is_shop_order_mode_enabled_on_variant": True}
            )
            .product_variant_id
        )
        cls.product.lst_price = 100

        cls.ProductPricelist = cls.env["product.pricelist"].with_context(
            queue_job__no_delay=True, ignore_es_update_role=True
        )

        date_start = date.today()
        date_end = date.today() + timedelta(days=30)
        cls.pricelist = cls.ProductPricelist.create(
            {
                "name": "PL",
                "item_ids": [
                    Command.create(
                        {
                            "applied_on": "3_global",
                            "compute_price": "percentage",
                            "percent_price": 10,
                            "date_start": date_start,
                            "date_end": date_end,
                        }
                    )
                ],
            }
        )

    def test_00(self):
        """Ensures the price field is empty for products only on quotation."""

        self.product.shop_order_mode = "quotation_only"
        product_schema = ProductProduct.from_product_product(self.product)
        self.assertFalse(
            product_schema.price, "Price should be empty for quotation-only products"
        )

        self.product.shop_order_mode = "direct_sale_only"
        product_schema = ProductProduct.from_product_product(self.product)
        self.assertTrue(
            product_schema.price,
            "Price should not be empty for direct sale only products",
        )

        self.product.shop_order_mode = "direct_sale_or_quotation"
        product_schema = ProductProduct.from_product_product(self.product)
        self.assertTrue(
            product_schema.price,
            "Price should not be empty for direct sale or quotation products",
        )

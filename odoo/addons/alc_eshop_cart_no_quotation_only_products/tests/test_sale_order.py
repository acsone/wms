# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestSaleOrder(TransactionCase):
    @classmethod
    def setUpClass(cls):
        # create a draft cart (sale_order)
        super().setUpClass()
        cls.product_1 = cls.env["product.product"].create(
            {
                "name": "product_1",
            }
        )
        cls.product_2 = (
            cls.env["product.template"]
            .create(
                {
                    "name": "product_2",
                    "shop_order_mode": "quotation_only",
                    "is_shop_order_mode_unabled_on_variant": True,
                }
            )
            .product_variant_id
        )
        partner = cls.env["res.partner"].create({"name": "Test Partner"})

        cls.cart = cls.env["sale.order"]._create_empty_cart(partner.id)
        cls.cart_with_quotation_only = cls.env["sale.order"]._create_empty_cart(
            partner.id
        )

        cls.cart.order_line = [
            Command.create(
                {
                    "product_id": cls.product_1.id,
                    "product_uom_qty": 1,
                }
            )
        ]
        cls.cart_with_quotation_only.order_line = [
            Command.create(
                {
                    "product_id": cls.product_1.id,
                    "product_uom_qty": 1,
                }
            ),
            Command.create(
                {
                    "product_id": cls.product_2.id,
                    "product_uom_qty": 1,
                }
            ),
        ]

    def test_cart_confirmation_blocked_when_quotation_only_product(self):
        self.assertEqual(self.cart.typology, "cart")
        self.assertEqual(self.cart_with_quotation_only.typology, "cart")

        # This cart should not be able to get confirmed because there is a "quotation_only" product inside
        with self.assertRaises(ValidationError):
            self.cart_with_quotation_only.action_confirm_cart()

        # This cart should be allowed to confirm since there is no "quotation_only" products
        try:
            self.cart.action_confirm_cart()
        except ValidationError:
            self.fail("action_confirm_cart() raised ValidationError unexpectedly!")

        self.assertEqual(self.cart.typology, "sale")

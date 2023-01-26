# Copyright 2018 Okia SPRL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import Command, fields
from odoo.tests.common import TransactionCase


class TestPurchaseOrder(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Create partner
        cls.partner = cls.env["res.partner"].create({"name": "Hello World"})

        cls.supplier = cls.env["res.partner"].create({"name": "Supplier"})

        # Create the main product
        cls.main_product = cls.env["product.product"].create(
            {"name": "Main product", "default_code": "1234567", "list_price": 100}
        )

        cls.additional_product = cls.env["product.product"].create(
            {"name": "Second product", "default_code": "987654321", "list_price": 20}
        )

        # Create the purchase_order
        cls.purchase_order = cls.env["purchase.order"].create(
            {
                "partner_id": cls.partner.id,
                "order_line": [
                    Command.create(
                        {
                            "name": cls.main_product.name,
                            "product_id": cls.main_product.id,
                            "product_uom": cls.env.ref("uom.product_uom_unit").id,
                            "product_qty": 12,
                            "sequence": 1,
                            "price_unit": 100,
                            "date_planned": fields.Datetime.now(),
                        },
                    )
                ],
            }
        )

    def test_action_confirm_1(self):
        """
        Confirm a purchase order without additional product.

        :return:
        """
        self.assertEqual(len(self.purchase_order.order_line), 1)

        self.purchase_order.button_confirm()
        self.assertEqual(len(self.purchase_order.order_line), 1)

    def test_button_compute_additional_products(self):
        """
        Set an additional product with ratio (5/2) and cancel this purchase.

        order
        :return:
        """
        self.main_product.write(
            {
                "ratio_main_product": 5,
                "ratio_additional_product": 2,
                "additional_product_id": self.additional_product.id,
            }
        )
        self.assertEqual(len(self.purchase_order.order_line), 1)

        self.purchase_order.button_compute_additional_products()
        self.assertEqual(len(self.purchase_order.order_line), 2)
        # Check main line
        main_line = self.purchase_order.order_line.filtered(
            lambda line: line.product_qty == 12.0
        )
        self.assertEqual(len(main_line), 1)
        self.assertEqual(main_line.price_unit, 100.0)
        # Check promotional line
        additional_line = self.purchase_order.order_line.filtered(
            lambda line: line.product_qty == 4.0
        )
        self.assertEqual(len(additional_line), 1)
        self.assertEqual(additional_line.price_unit, 0.0)

        # Cancel the PO
        self.purchase_order.button_draft()
        self.assertEqual(len(self.purchase_order.order_line), 1)
        # Check main line
        main_line = self.purchase_order.order_line.filtered(
            lambda line: line.product_qty == 12.0
        )
        self.assertEqual(len(main_line), 1)
        # Check promotional line
        additional_line = self.purchase_order.order_line.filtered(
            lambda line: line.product_qty == 4.0
        )
        self.assertEqual(len(additional_line), 0)

# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.fields import Command
from odoo.tests import Form, TransactionCase


class TestPurchaseOrderBuilder(TransactionCase):

    # TODO: Add full test stack in this module

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product_obj = cls.env["product.product"]
        cls.purchase_obj = cls.env["purchase.order"]
        cls.supplier = cls.env["res.partner"].create(
            {
                "name": "Supplier 1",
            }
        )

        cls.product = cls.product_obj.create(
            {
                "name": "Product 1",
                "seller_ids": [
                    Command.create(
                        {
                            "partner_id": cls.supplier.id,
                            "price": 10.0,
                        }
                    ),
                    Command.create(
                        {
                            "partner_id": cls.supplier.id,
                            "price": 10.0,
                            "discount": 5.0,
                        }
                    ),
                    Command.create(
                        {
                            "partner_id": cls.supplier.id,
                            "price": 10.0,
                            "discount": 10.0,
                            "date_start": "2023-01-01",
                            "date_end": "2023-01-05",
                        }
                    ),
                ],
            }
        )

    @classmethod
    def _create_purchase(cls):
        cls.purchase = cls.purchase_obj.create(
            {
                "partner_id": cls.supplier.id,
            }
        )
        with Form(cls.purchase) as purchase_form:
            with Form(purchase_form.order_line.new()) as line_form:
                line_form.product_id = cls.product
                line_form.product_uom_qty = 5.0

    def test_promotions(self):
        # Test we retrieve the promotion lines
        promotions = self.product.get_promotions()
        self.assertEqual(len(promotions), 2)
        self.assertFalse(
            promotions[0].date_start,
        )
        self.assertEqual(promotions[1].discount, 10.0)

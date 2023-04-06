# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import Command
from odoo.tests.common import TransactionCase


class TestPurchaseOrderTotalWeight(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.product = cls.env["product.product"].create(
            {"name": "Unittest P", "weight": 0.5}
        )
        cls.partner = cls.env["res.partner"].create({"name": "Unittest partner"})

    def test_1(self):
        """Test purchase order total weight."""
        po = self.env["purchase.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    Command.create(
                        {"product_id": self.product.id, "product_qty": 10},
                    ),
                    Command.create(
                        {"product_id": self.product.id, "product_qty": 15},
                    ),
                ],
            }
        )
        self.assertEqual(po.total_weight, 0.5 * 10 + 0.5 * 15)
        po.order_line[0].product_qty = 20
        self.assertEqual(po.total_weight, 0.5 * 20 + 0.5 * 15)
        po.order_line.unlink()
        self.assertEqual(po.total_weight, 0)

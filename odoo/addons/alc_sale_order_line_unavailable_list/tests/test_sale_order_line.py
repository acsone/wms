# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.fields import Command

from odoo.addons.base.tests.common import BaseCommon


class TestSaleOrderLineUnavailable(BaseCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env["sale.order"].search([("state", "=", "draft")])._action_cancel()
        cls.exception = cls.env.ref("sale_exception.exception_product_sale_warning")
        cls.exception.active = True
        cls.product = cls.env["product.product"].create(
            {"name": "Product Test", "sale_line_warn": "warning"}
        )

        cls.sale_1 = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "date_order": "2024-12-01",
                "order_line": [
                    Command.create(
                        {
                            "product_id": cls.product.id,
                            "exception_ids": [Command.set(cls.exception.ids)],
                        }
                    )
                ],
            }
        )
        cls.sale_2 = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "date_order": "2024-12-02",
                "order_line": [
                    Command.create(
                        {
                            "product_id": cls.product.id,
                        }
                    )
                ],
            }
        )

        cls.sale_1.order_line.detect_exceptions()
        cls.sale_1.detect_exceptions()

    def test_sale_order(self):
        """
        Search for sale order lines.

        Sale order 1 line has exception and should appear first.

        Then, search with the context for the action.

        Sale order 2 line should appear first.
        """
        lines = self.env["sale.order.line"].search([("state", "=", "draft")])

        self.assertEqual(self.sale_1.order_line, lines[0])
        self.assertEqual(self.sale_2.order_line, lines[1])

        lines = (
            self.env["sale.order.line"]
            .with_context(unavailable_list=True)
            .search([("state", "=", "draft")])
        )

        self.assertEqual(self.sale_2.order_line, lines[0])
        self.assertEqual(self.sale_1.order_line, lines[1])

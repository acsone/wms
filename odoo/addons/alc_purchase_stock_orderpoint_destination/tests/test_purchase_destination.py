# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.fields import Command

from odoo.addons.base.tests.common import BaseCommon


class TestPurchaseDestination(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.orderpoint_obj = cls.env["stock.warehouse.orderpoint"]
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Supplier",
            }
        )
        cls.buy = cls.env["stock.rule"].search(
            [
                ("action", "=", "buy"),
                ("location_dest_id", "=", cls.warehouse.lot_stock_id.id),
            ]
        )
        cls.buy.location_dest_id = cls.warehouse.view_location_id
        cls.product = cls.env["product.product"].create(
            {
                "name": "Product Test",
                "type": "product",
                "route_ids": [Command.link(cls.buy.route_id.id)],
                "seller_ids": [
                    Command.create(
                        {
                            "partner_id": cls.partner.id,
                            "product_code": "P TEST",
                        }
                    )
                ],
            }
        )

        # Create orderpoint
        cls.orderpoint = cls.orderpoint_obj.create(
            {
                "product_id": cls.product.id,
                "location_id": cls.warehouse.view_location_id.id,
                "product_min_qty": 10.0,
                "product_max_qty": 20.0,
            }
        )

    def test_purchase_destination(self):
        """
        Check that the destination location for purchase moves.

        are Stock and not the view_location_id of Warehouse (WH)
        """
        self.orderpoint._procure_orderpoint_confirm(company_id=self.env.company)
        line = self.env["purchase.order.line"].search(
            [("product_id", "=", self.product.id)]
        )
        self.assertTrue(line)
        self.assertNotEqual(
            line.order_id.dest_address_id.property_stock_customer,
            self.warehouse.view_location_id,
        )
        line.order_id.button_approve()
        self.assertEqual(line.move_ids.location_dest_id, self.warehouse.lot_stock_id)

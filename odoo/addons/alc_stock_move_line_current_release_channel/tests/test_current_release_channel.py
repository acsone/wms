# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.fields import Command

from odoo.addons.base.tests.common import BaseCommon


class TestCurrentRelease(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.customer = cls.env.ref("stock.stock_location_customers")
        cls.stock = cls.env.ref("stock.stock_location_stock")
        cls.product_obj = cls.env["product.product"]
        cls.default_channel = cls.env.ref(
            "stock_release_channel.stock_release_channel_default"
        )
        cls.warehouse.delivery_steps = "pick_ship"

        cls.product_1 = cls.product_obj.create(
            {
                "name": "Product 1",
                "type": "product",
                "route_ids": [Command.link(cls.warehouse.delivery_route_id.id)],
            }
        )

        cls.product_2 = cls.product_obj.create(
            {
                "name": "Product 2",
                "type": "product",
                "route_ids": [Command.link(cls.warehouse.delivery_route_id.id)],
            }
        )

        cls.warehouse.delivery_route_id.available_to_promise_defer_pull = True

    @classmethod
    def _create_quantity(cls, product, quantity):
        cls.env["stock.quant"].with_context(inventory_mode=True).create(
            {
                "product_id": product.id,
                "inventory_quantity": quantity,
                "location_id": cls.stock.id,
            }
        )._apply_inventory()

    def test_current_release_channel(self):
        """
        Create a procurement on Customers location for both Product 1 and Product 2.

        Create a stock quantity for product 1 only
        Release the picking OUT
        Check the current_release_channel field is True for INT move for product 1

        Transfer the whole product 1 moves (INT and OUT)
        Release the backorder

        Check the current_release_channel field is True for INT move for product 2

        Check the current_release_channel field is False for INT move for product 1
        """
        self._create_quantity(self.product_1, 10.0)
        self.move_before_1 = self.env["stock.move"].search(
            [
                ("product_id", "=", self.product_1.id),
                ("location_dest_id", "=", self.customer.id),
            ]
        )
        self.move_before_2 = self.env["stock.move"].search(
            [
                ("product_id", "=", self.product_2.id),
                ("location_dest_id", "=", self.customer.id),
            ]
        )
        proc_vals = {}
        self.env["procurement.group"].run(
            [
                self.env["procurement.group"].Procurement(
                    self.product_1,
                    10.0,
                    self.product_1.uom_id,
                    self.customer,
                    "Test 1",
                    "Test 1",
                    self.env.company,
                    proc_vals,
                ),
                self.env["procurement.group"].Procurement(
                    self.product_2,
                    10.0,
                    self.product_2.uom_id,
                    self.customer,
                    "Test 2",
                    "Test 2",
                    self.env.company,
                    proc_vals,
                ),
            ]
        )

        self.move_out_1 = (
            self.env["stock.move"].search(
                [
                    ("product_id", "=", self.product_1.id),
                    ("location_dest_id", "=", self.customer.id),
                ]
            )
            - self.move_before_1
        )
        self.move_out_2 = (
            self.env["stock.move"].search(
                [
                    ("product_id", "=", self.product_2.id),
                    ("location_dest_id", "=", self.customer.id),
                ]
            )
            - self.move_before_2
        )

        self.assertTrue(self.move_out_1)
        self.move_out_1.picking_id.release_channel_id = self.default_channel
        self.move_out_1.picking_id.release_available_to_promise()

        self.assertTrue(self.move_out_1.move_orig_ids)

        self.assertTrue(
            self.move_out_1.move_orig_ids.move_line_ids.current_release_channel
        )

        # Transfer the stock picking, then the out with a backorder
        self.move_out_1.move_orig_ids.move_line_ids.qty_done = 10.0
        self.move_out_1.move_orig_ids.picking_id._action_done()

        self.move_out_1.move_line_ids.qty_done = 10.0
        self.move_out_1.picking_id._action_done()

        backorder_out = self.move_out_1.picking_id.backorder_ids
        self.assertTrue(backorder_out)

        backorder_out.unrelease()

        # Set quantity on Stock for product 2
        self._create_quantity(self.product_2, 10.0)
        backorder_out.move_ids.invalidate_recordset()

        backorder_out.release_available_to_promise()

        self.assertTrue(self.move_out_2.move_orig_ids)
        self.assertTrue(self.move_out_2.move_orig_ids.move_line_ids)
        self.assertTrue(
            self.move_out_2.move_orig_ids.move_line_ids.current_release_channel
        )
        move_lines = self.env["stock.move.line"].search(
            [
                ("current_release_channel", "=", True),
                ("id", "in", self.move_out_2.move_orig_ids.move_line_ids.ids),
            ]
        )
        self.assertTrue(move_lines)
        self.assertEqual(move_lines, self.move_out_2.move_orig_ids.move_line_ids)
        self.move_out_1.move_line_ids.invalidate_recordset()
        self.assertFalse(self.move_out_1.move_line_ids.current_release_channel)

        # Check multi call
        (
            self.move_out_1.move_line_ids | self.move_out_2.move_orig_ids.move_line_ids
        ).invalidate_recordset()
        currents = (
            self.move_out_1.move_line_ids | self.move_out_2.move_orig_ids.move_line_ids
        ).mapped("current_release_channel")
        self.assertEqual([False, True], currents)

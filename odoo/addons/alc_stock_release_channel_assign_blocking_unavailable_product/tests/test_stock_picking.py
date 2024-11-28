# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command

from odoo.addons.base.tests.common import BaseCommon

from .common import StockReleaseChannelBlockingCommon


class TestStockPicking(StockReleaseChannelBlockingCommon, BaseCommon):

    def test_00(self):
        """Create backorder and check that it's flagged as full backorder."""
        self.sale.action_confirm()
        self.picking = self.sale.picking_ids
        self._do_picking(self.picking, 100)
        self.assertEqual(self.picking.state, "done")
        self.backorder = self.picking.backorder_ids
        self.assertTrue(self.backorder.move_ids.delivery_requires_other_lines)
        self.assertEqual(self.backorder.move_ids.product_qty_unavailable, 20)
        self.assertTrue(self.backorder.delivery_requires_other_lines)
        self.assertTrue(self.backorder.blocked_for_channel_assignation)

    def test_01(self):
        """Check that a full backorder became a regular picking if new move is added."""
        self.test_00()
        self.env["stock.move"].create(
            {
                "picking_id": self.backorder.id,
                "name": "Delivery move",
                "product_id": self.product.id,
                "product_uom_qty": 120,
                "product_uom": self.product.uom_id.id,
                "location_id": self.loc_stock.id,
                "location_dest_id": self.loc_customer.id,
                "picking_type_id": self.env.ref("stock.picking_type_out").id,
            }
        )
        self.assertFalse(self.backorder.delivery_requires_other_lines)
        self.assertFalse(self.backorder.blocked_for_channel_assignation)

    def test_02(self):
        """Check that a full back order can't be assigned to a release channel."""
        self.test_00()
        self.backorder.assign_release_channel()
        self.assertFalse(self.backorder.release_channel_id)

    def test_03(self):
        """Check that a mixed back order can be assigned to a release channel."""
        self.test_01()
        self.backorder.assign_release_channel()
        self.assertTrue(self.backorder.release_channel_id)

    def test_04(self):
        """Check that a full back order can be assigned to a release channel if user.

        force it
        """
        self.test_00()
        self.backorder.button_ignore_release_channel_block()
        self.assertTrue(self.backorder.release_channel_id)
        self.assertFalse(self.backorder.blocked_for_channel_assignation)

    def test_05(self):
        """Create backorder even if the product is available, the backorder should be.

        assigned and not flagged as full back order
        """
        self.assertEqual(self.sale.order_line.product_qty_unavailable, 20)
        self.sale.order_line.product_uom_qty = 100
        self.assertEqual(self.sale.order_line.product_qty_unavailable, 0.0)
        self.sale.action_confirm()
        self.picking = self.sale.picking_ids
        self._do_picking(self.picking, 80)
        self.assertEqual(self.picking.state, "done")
        self.backorder = self.picking.backorder_ids
        self.assertFalse(self.backorder.move_ids.delivery_requires_other_lines)
        self.assertEqual(self.backorder.move_ids.product_qty_unavailable, 0)
        self.assertFalse(self.backorder.delivery_requires_other_lines)
        self.backorder.assign_release_channel()
        self.assertTrue(self.backorder.release_channel_id)

    def test_06(self):
        """Users can prevent a sale order from being delivered individually."""
        self.sale.order_line.product_uom_qty = 20
        self.assertEqual(self.sale.order_line.product_qty_unavailable, 0)
        self.sale.do_not_deliver_if_alone = True
        self.sale.action_confirm()
        self.picking = self.sale.picking_ids
        self.assertTrue(self.picking.move_ids.delivery_requires_other_lines)
        self.assertTrue(self.picking.delivery_requires_other_lines)
        self.picking.assign_release_channel()
        self.assertFalse(self.picking.release_channel_id)

    def test_several_orders_with_backorder(self):
        """
        The use case is the following:

        - Create a sale order with two products, one available, one unavailable
        - Deliver the available product and create a backorder for the other
        - Replenish product 2
        - Modify the sale order to add the available product again
        - Assign the release channel
        - The release channel should be assigned to the backorder
        """
        # Use a part of first product avialability
        self.sale.order_line.write({"product_uom_qty": 50.0})
        # Create a line for the second product
        self.sale.write(
            {
                "order_line": [
                    Command.create(
                        {
                            "name": self.product.name,
                            "product_id": self.product_2.id,
                            "product_uom_qty": 120,
                        },
                    )
                ],
            }
        )
        # Necessary to recompute
        self.sale.order_line.flush_recordset()
        self.sale.action_confirm()
        line1 = self.sale.order_line.filtered(
            lambda line: line.product_id == self.product
        )
        line2 = self.sale.order_line.filtered(
            lambda line: line.product_id == self.product_2
        )
        self.assertEqual(0.0, line1.product_qty_unavailable)
        self.assertEqual(120.0, line2.product_qty_unavailable)

        picking = self.sale.picking_ids

        self.assertEqual("assigned", picking.state)

        picking.move_line_ids.filtered(
            lambda line: line.product_id == self.product
        ).qty_done = 50.0
        picking._action_done()

        self.assertEqual(picking.state, "done")
        backorder = picking.backorder_ids
        self.assertTrue(backorder)

        # Replenish product 2
        self.env["stock.quant"]._update_available_quantity(
            self.product_2, self.loc_stock, 120.0
        )

        # relaunch a procurement
        line1.product_uom_qty = 100.0

        backorder.assign_release_channel()
        self.assertTrue(backorder.release_channel_id)

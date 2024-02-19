# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.tests.common import TransactionCase


class TestStockPicking(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env["product.product"].create(
            {"name": "product", "type": "product"}
        )
        cls.wh = cls.env.ref("stock.warehouse0")
        cls.loc_stock = cls.wh.lot_stock_id
        cls.loc_customer = cls.env.ref("stock.stock_location_customers")
        cls.env["stock.quant"]._update_available_quantity(
            cls.product, cls.loc_stock, 100.0
        )
        cls.partner = cls.env["res.partner"].create({"name": "Unittest partner"})
        cls.sale = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "order_line": [
                    Command.create(
                        {
                            "name": cls.product.name,
                            "product_id": cls.product.id,
                            "product_uom_qty": 120,
                        },
                    )
                ],
            }
        )

    @classmethod
    def _do_picking(cls, picking, done_qty):
        picking.move_ids.quantity_done = done_qty
        picking._action_done()

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

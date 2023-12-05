# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.fields import Command
from odoo.tests.common import TransactionCase


class TestPickingBackorderNoUser(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.stock = cls.env.ref("stock.stock_location_stock")
        cls.customers = cls.env.ref("stock.stock_location_customers")
        cls.demo = cls.env.ref("base.user_demo")
        cls.product = cls.env["product.product"].create(
            {
                "name": "No Backorder user product",
                "type": "product",
            }
        )
        cls.env["stock.quant"].create(
            {
                "product_id": cls.product.id,
                "location_id": cls.stock.id,
                "inventory_quantity": 50.0,
            }
        )._apply_inventory()

    @classmethod
    def _create_picking(cls):
        cls.picking = cls.env["stock.picking"].create(
            {
                "location_id": cls.stock.id,
                "location_dest_id": cls.customers.id,
                "picking_type_id": cls.env.ref("stock.picking_type_out").id,
                "move_ids": [
                    Command.create(
                        {
                            "name": "Product",
                            "location_id": cls.stock.id,
                            "location_dest_id": cls.customers.id,
                            "product_id": cls.product.id,
                            "product_uom": cls.product.uom_id.id,
                            "product_uom_qty": 5.0,
                        }
                    )
                ],
            }
        )

    def test_backorder_no_user(self):
        # Activate the feature
        self.env.company.no_user_on_backorder = True
        self._create_picking()
        self.picking.action_confirm()
        # Affect a user to the picking
        self.picking.user_id = self.demo
        self.assertEqual(self.picking.user_id, self.demo)
        self.picking.move_line_ids.qty_done = 4.0
        self.picking._action_done()
        self.assertTrue(self.picking.backorder_ids)
        self.assertFalse(self.picking.backorder_ids.user_id)

    def test_backorder_user(self):
        # Check user is kept on backorder
        self._create_picking()
        self.picking.action_confirm()
        # Affect a user to the picking
        self.picking.user_id = self.demo
        self.assertEqual(self.picking.user_id, self.demo)
        self.picking.move_line_ids.qty_done = 4.0
        self.picking._action_done()
        self.assertTrue(self.picking.backorder_ids)
        self.assertEqual(self.picking.user_id, self.demo)

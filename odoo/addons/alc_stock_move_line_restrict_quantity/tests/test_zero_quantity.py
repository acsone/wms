# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.exceptions import UserError
from odoo.fields import Command
from odoo.tests.common import TransactionCase


class TestZeroQuantity(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.customers = cls.env.ref("stock.stock_location_customers")
        cls.product = cls.env["product.product"].create(
            {
                "name": "Product 1",
                "type": "product",
                "tracking": "lot",
            }
        )
        cls.lot = cls.env["stock.lot"].create(
            {
                "name": "Lot 1",
                "product_id": cls.product.id,
            }
        )
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Partner 1",
            }
        )
        cls.picking = cls.env["stock.picking"].create(
            {
                "partner_id": cls.partner.id,
                "location_id": cls.warehouse.lot_stock_id.id,
                "location_dest_id": cls.customers.id,
                "picking_type_id": cls.warehouse.out_type_id.id,
                "move_ids": [
                    Command.create(
                        {
                            "name": "Product 1",
                            "location_id": cls.warehouse.lot_stock_id.id,
                            "location_dest_id": cls.customers.id,
                            "product_id": cls.product.id,
                            "product_uom_qty": 10.0,
                            "product_uom": cls.product.uom_id.id,
                        }
                    )
                ],
            }
        )

    @classmethod
    def _create_quantity(cls, product, qty, lot=None):
        cls.env["stock.quant"].with_context(inventory_mode=True).create(
            {
                "product_id": product.id,
                "inventory_quantity": qty,
                "location_id": cls.warehouse.lot_stock_id.id,
                "lot_id": lot.id if lot else cls.lot.id,
            }
        )._apply_inventory()

    def test_zero(self):
        # Enable the feature
        self.env.company.restrict_move_line_quantity = True
        self._create_quantity(self.product, 10.0)
        self.picking.action_confirm()
        self.picking.action_assign()
        self.picking.move_line_ids.qty_done = 10.0

        with self.assertLogs(level="ERROR") as log_catcher, self.assertRaises(
            UserError
        ):
            self._create_quantity(self.product, 0.0)
        self.assertEqual(
            len(log_catcher.output), 1, "Exactly one error should be logged"
        )
        self.assertIn(
            f"The demand quantity should not be set to 0 or negative in the picking {self.picking.name} for product {self.product.name}",
            log_catcher.output[0],
        )

    def test_zero_just_log(self):
        # Just log
        self._create_quantity(self.product, 10.0)
        self.picking.action_confirm()
        self.picking.action_assign()
        self.picking.move_line_ids.qty_done = 10.0

        with self.assertLogs(level="ERROR") as log_catcher:
            self._create_quantity(self.product, 0.0)
        self.assertEqual(
            len(log_catcher.output), 1, "Exactly one error should be logged"
        )
        self.assertIn(
            f"The demand quantity should not be set to 0 or negative in the picking {self.picking.name} for product {self.product.name}",
            log_catcher.output[0],
        )

    def test_negative(self):
        # Enable the feature and check negative
        self.env.company.restrict_move_line_quantity = True
        self._create_quantity(self.product, 10.0)
        self.picking.action_confirm()
        self.picking.action_assign()
        self.picking.move_line_ids.qty_done = 10.0

        with self.assertLogs(level="ERROR") as log_catcher, self.assertRaises(
            UserError
        ):
            self._create_quantity(self.product, -1.0)
        self.assertEqual(
            len(log_catcher.output), 1, "Exactly one error should be logged"
        )
        self.assertIn(
            f"The demand quantity should not be set to 0 or negative in the picking {self.picking.name} for product {self.product.name}",
            log_catcher.output[0],
        )

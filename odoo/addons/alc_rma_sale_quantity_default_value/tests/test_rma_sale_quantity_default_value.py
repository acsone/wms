# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.tests.common import TransactionCase


class TestRmaSaleQuantityDefaultValue(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.loc_stock = cls.warehouse.lot_stock_id
        cls.partner1 = cls.env["res.partner"].create({"name": "Partner"})
        cls.p1 = cls.env["product.product"].create(
            {"name": "Unittest P1", "type": "product"}
        )
        cls.so = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner1.id,
                "order_line": [
                    Command.create(
                        {
                            "name": cls.p1.name,
                            "product_id": cls.p1.id,
                            "product_uom_qty": 5,
                            "price_unit": 50,
                        },
                    )
                ],
            }
        )
        cls.env["stock.quant"].with_context(inventory_mode=True).create(
            {
                "product_id": cls.p1.id,
                "inventory_quantity": 10,
                "location_id": cls.loc_stock.id,
            }
        )._apply_inventory()
        cls.so.action_confirm()
        cls.picking = cls.so.picking_ids[0]

    def _get_rma_wizard(self):
        action = self.so.action_create_rma()
        return self.env[action.get("res_model")].browse(action.get("res_id"))

    def test_1(self):
        """
        Test rma wizard:

            - fully deliver the so
            - open rma wizard
        expected:
            - qty proposed: 0
            - allowed qty 5
        """
        self.picking.action_set_quantities_to_reservation()
        self.picking._action_done()
        self.assertEqual(self.picking.state, "done")
        self.assertEqual(self.so.order_line.qty_delivered, 5)
        wizard = self._get_rma_wizard()
        self.assertEqual(len(wizard.line_ids), 1)
        self.assertEqual(wizard.line_ids.quantity, 0)
        self.assertEqual(wizard.line_ids.allowed_quantity, 5)

    def test_2(self):
        """
        Test rma wizard:

            - partially deliver the so
            - open rma wizard
        expected:
            - qty proposed: 0
            - allowed qty 3
        """
        self.picking.move_line_ids.qty_done = 3
        self.picking._action_done()
        self.assertEqual(self.picking.state, "done")
        self.assertEqual(self.so.order_line.qty_delivered, 3)
        wizard = self._get_rma_wizard()
        self.assertEqual(len(wizard.line_ids), 1)
        self.assertEqual(wizard.line_ids.quantity, 0)
        self.assertEqual(wizard.line_ids.allowed_quantity, 3)

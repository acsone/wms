# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.tests.common import TransactionCase


class TestRmaOriginalPickingResponsible(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.admin_user = cls.env.ref("base.user_admin")
        cls.demo_user = cls.env.ref("base.user_demo")
        cls.partner = cls.env["res.partner"].create({"name": "partner"})
        cls.operation = cls.env.ref("rma.rma_operation_replace")
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.warehouse.delivery_steps = "pick_ship"
        cls.loc_stock = cls.warehouse.lot_stock_id
        cls.product = cls.env["product.product"].create(
            {"name": "product", "type": "product"}
        )
        cls.env["stock.quant"]._update_available_quantity(cls.product, cls.loc_stock, 5)
        cls.so = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "warehouse_id": cls.warehouse.id,
                "order_line": [
                    Command.create(
                        {
                            "name": cls.product.name,
                            "product_id": cls.product.id,
                            "product_uom_qty": 5,
                            "product_uom": cls.product.uom_id.id,
                            "price_unit": 1,
                        },
                    )
                ],
            }
        )
        cls.so.action_confirm()
        cls.so.action_done()
        cls.pick = cls.so.picking_ids.filtered(
            lambda p: p.picking_type_id.code == "internal"
        )
        cls.out = cls.so.picking_ids.filtered(
            lambda p: p.picking_type_id.code == "outgoing"
        )
        cls._do_transfer(cls.pick, 2)
        cls._do_transfer(cls.pick.backorder_ids, 3)
        cls._do_transfer(cls.out, 5)
        cls.pick.user_id = cls.demo_user
        cls.pick.backorder_ids.user_id = cls.admin_user
        wizard_id = cls.so.action_create_rma()["res_id"]
        wizard = cls.env["sale.order.rma.wizard"].browse(wizard_id)
        wizard.operation_id = cls.operation
        cls.rma = cls.env["rma"].browse(wizard.create_and_open_rma()["res_id"])

    @classmethod
    def _do_transfer(cls, pick, quantity):
        pick.move_line_ids.qty_done = quantity
        pick._action_done()

    def test_0(self):
        self.assertEqual(self.rma.order_id, self.so)
        self.assertEqual(
            self.rma.internal_picking_ids, self.pick + self.pick.backorder_ids
        )
        self.assertEqual(
            self.rma.internal_picking_user_ids, self.demo_user + self.admin_user
        )
        self.assertEqual(self.rma.internal_picking_id, self.pick)
        self.assertEqual(self.rma.internal_picking_user_id, self.demo_user)

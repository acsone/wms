# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError
from odoo.tests.common import SavepointCase


class TestSaleCancelRemaining(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestSaleCancelRemaining, cls).setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context, tracking_disable=True, test_queue_job_no_delay=True
            )
        )
        cls.partner = cls.env["res.partner"].create({"name": "Partner"})
        cls.warehouse_1 = cls.env.ref("stock.warehouse0")
        cls.warehouse_1.write(
            {
                "name": "Test Warehouse",
                "reception_steps": "one_step",
                "delivery_steps": "pick_ship",
                "code": "TST",
            }
        )
        cls.warehouse_1.pick_type_id.subcode = "PICK"
        cls.product_1 = cls.env["product.product"].create(
            {
                "name": "test product 1",
                "type": "product",
                "sale_ok": True,
                "active": True,
            }
        )

        cls.product_2 = cls.env["product.product"].create(
            {
                "name": "test product 2",
                "type": "product",
                "sale_ok": True,
                "active": True,
            }
        )

        cls.product_3 = cls.env["product.product"].create(
            {
                "name": "test product 3",
                "type": "product",
                "sale_ok": True,
                "active": True,
            }
        )

        cls.sale = cls._confirm_sale_order()
        cls.wiz = cls.env["cancel.remaining.wizard"].create({})

    @classmethod
    def _confirm_sale_order(
        cls, partner=None, product=None, qty=10, picking_policy="direct"
    ):
        if partner is None:
            partner = cls.partner
        if product is None:
            product = cls.product_1
        warehouse = cls.warehouse_1
        Sale = cls.env["sale.order"]
        lines = [
            (
                0,
                0,
                {
                    "name": p.name,
                    "product_id": p.id,
                    "product_uom_qty": qty,
                    "product_uom": p.uom_id.id,
                    "price_unit": 1,
                },
            )
            for p in product
        ]
        so_values = {
            "partner_id": partner.id,
            "warehouse_id": warehouse.id,
            "order_line": lines,
        }
        if picking_policy:
            so_values["picking_policy"] = picking_policy
        so = Sale.create(so_values)
        so.action_confirm()
        return so

    def test_00_cancel_remaining_qty_not_started_picking(self):
        line = self.sale.order_line
        self.assertEqual(line.product_qty_remains_to_deliver, 10)
        self.assertEqual(line.product_qty_canceled, 0)
        self.wiz.with_context(active_id=line.id).cancel_remaining_qty()

        self.assertEqual(line.product_qty_remains_to_deliver, 0)
        self.assertEqual(line.product_qty_canceled, 10)

    def test_01_cancel_remaining_qty_started_picking(self):
        pick = self.sale.picking_ids.filtered(
            lambda picking: picking.picking_type_code == "internal"
            and picking.state not in ("cancel", "done")
        )
        pick.printed = True
        with self.assertRaises(UserError):
            self.wiz.with_context(
                active_id=self.sale.order_line.id
            ).cancel_remaining_qty()

    def test_02_cancel_remaining_qty_for_backorder_all_at_once(self):

        sale2 = self._confirm_sale_order(picking_policy="one")
        line = sale2.order_line
        pick = sale2.picking_ids.filtered(
            lambda picking: picking.picking_type_code == "internal"
            and picking.state not in ("cancel", "done")
        )
        backorder = pick._create_backorder()

        backorder.with_context(force_cancel=True).action_cancel()
        self.wiz.with_context(active_id=sale2.order_line.id).cancel_remaining_qty()
        self.assertEqual(line.product_qty_remains_to_deliver, 0)
        self.assertEqual(line.product_qty_canceled, 10)

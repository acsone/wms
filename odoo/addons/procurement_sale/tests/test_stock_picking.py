# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestStockPicking(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestStockPicking, cls).setUpClass()
        cls.env = cls.env(
            context=dict(cls.env.context, tracking_disable=True, round_autoset=False)
        )
        cls.partner1 = cls.env["res.partner"].create(
            {"name": "Unittest partner", "ref": "12344566777878"}
        )
        cls.p1 = cls.env["product.product"].create(
            {
                "name": "Unittest P1",
                "uom_id": cls.env.ref("product.product_uom_unit").id,
                "type": "product",
                "weight": 10.0,
            }
        )
        cls.warehouse_1 = cls.env["stock.warehouse"].create(
            {
                "name": "Base Warehouse",
                "reception_steps": "one_step",
                "delivery_steps": "pick_ship",
                "code": "BWH",
            }
        )
        inventory = cls.env["stock.inventory"].create(
            {"name": "Test", "product_id": cls.p1.id, "filter": "product"}
        )
        inventory.prepare_inventory()
        cls.env["stock.inventory.line"].create(
            {
                "inventory_id": inventory.id,
                "product_id": cls.p1.id,
                "product_uom_id": cls.env.ref("product.product_uom_unit").id,
                "product_qty": 100,
                "location_id": cls.warehouse_1.lot_stock_id.id,
            }
        )
        inventory.action_done()
        # The reservation is conditional to the subcode...??? BEURK
        cls.warehouse_1.pick_type_id.subcode = "PICK"

    @classmethod
    def _confirm_sale_order(cls, partner=None, product=None, qty=1, carrier_id=None):
        if partner is None:
            partner = cls.partner1
        if product is None:
            product = cls.p1
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
        if carrier_id:
            so_values["carrier_id"] = carrier_id
        so = Sale.create(so_values)
        so.action_confirm()
        return so

    def test_00(self):
        """
        Data:
            A warehouse with 2 steps pcicking
            A product with 100 in stock
        Test Case
            Create and confirm a SO for 75
        Expected Result:
            PAck operations (therefore reservation) exists into the pick
            and ship picking
        -> into this test we ensure that the move for a chained picking
        doesn't block the initial picking. Indeed when we compute the reservation
        for the PICK picking, a move with the same qty and same date already
        exist for the SHIP picking. This move must be ignored from the list
        of previous picking since it's linked to the first one.
        """
        so1 = self._confirm_sale_order(self.partner1, product=self.p1, qty=75)
        self.assertEqual(so1.mapped("picking_ids.move_lines.product_id"), self.p1)
        pick = so1.picking_ids.filtered(
            lambda p: p.picking_type_id == self.warehouse_1.pick_type_id
        )
        self.assertTrue(pick)
        pick.action_assign()
        self.assertEqual(len(pick.pack_operation_ids), 1)
        self.assertEqual(pick.pack_operation_ids.product_qty, 75)

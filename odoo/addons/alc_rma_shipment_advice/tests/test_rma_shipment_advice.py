# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.rma_sale.tests.test_rma_sale import TestRmaSaleBase


class TestRmaShipmentAdvice(TestRmaSaleBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        stock_location = cls.env.ref("stock.stock_location_stock")
        cls.env["stock.quant"]._update_available_quantity(
            cls.product_1, stock_location, 10
        )
        sale_order = cls._create_sale_order(cls, [[cls.product_1, 5]])
        sale_order.action_confirm()
        order_out_picking = sale_order.picking_ids
        order_out_picking.move_ids.quantity_done = 5
        order_out_picking.button_validate()
        wizard_id = sale_order.action_create_rma()["res_id"]
        wizard = cls.env["sale.order.rma.wizard"].browse(wizard_id)
        wizard.operation_id = cls.operation
        rma = cls.env["rma"].browse(wizard.create_and_open_rma()["res_id"])
        cls.rma_picking = rma.reception_move_id.picking_id
        cls.sale_order = cls._create_sale_order(cls, [[cls.product_1, 5]])
        cls.sale_order.action_confirm()
        cls.order_out_picking = cls.sale_order.picking_ids
        cls.dock = cls.env.ref("shipment_advice.stock_dock_demo")
        cls.shipment_advice = cls.env["shipment.advice"].create(
            {
                "shipment_type": "outgoing",
                "arrival_date": "2024-01-01",
                "dock_id": cls.dock.id,
            }
        )
        cls.shipment_advice.action_confirm()
        cls.order_out_picking._plan_in_shipment(cls.shipment_advice)
        cls.order_out_picking._load_in_shipment(cls.shipment_advice)

    def test_0(self):
        self.assertTrue(self.rma_picking)
        self.assertEqual(self.shipment_advice.state, "confirmed")
        self.assertEqual(
            self.shipment_advice.planned_picking_ids, self.order_out_picking
        )
        self.assertEqual(
            self.shipment_advice.loaded_picking_ids, self.order_out_picking
        )

    def test_1(self):
        self.shipment_advice.action_in_progress()
        self.shipment_advice.action_done()
        self.assertEqual(self.shipment_advice.state, "done")
        self.assertFalse(self.shipment_advice.rma_picking_ids)

    def test_2(self):
        self.order_out_picking.toursolver_shipment_advice_rank = 9
        self.rma_picking.picking_type_id.is_rma = True
        self.shipment_advice.action_in_progress()
        self.shipment_advice.action_done()
        self.assertEqual(self.shipment_advice.state, "done")
        self.assertEqual(self.shipment_advice.rma_picking_ids, self.rma_picking)
        self.assertEqual(self.shipment_advice.rma_pickings_count, 1)
        action = self.shipment_advice.button_open_rma_pickings()
        self.assertEqual(action.get("domain"), [("id", "in", self.rma_picking.ids)])
        self.assertEqual(self.rma_picking.toursolver_shipment_advice_rank, 9)

    def test_3(self):
        self.rma_picking.partner_id = self.env["res.partner"].create(
            {"name": "different partner"}
        )
        self.shipment_advice.action_in_progress()
        self.shipment_advice.action_done()
        self.assertEqual(self.shipment_advice.state, "done")
        self.assertFalse(self.shipment_advice.rma_picking_ids)

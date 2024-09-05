# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import Form

from odoo.addons.rma_sale.tests.test_rma_sale import TestRmaSaleBase


class TestRmaOperationReturnLocation(TestRmaSaleBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.sale_order = cls._create_sale_order(cls, [[cls.product_1, 5]])
        cls.sale_order.action_confirm()
        cls.order_out_picking = cls.sale_order.picking_ids
        cls.order_out_picking.move_ids.quantity_done = 5
        cls.order_out_picking.button_validate()
        cls.wh = cls.env.ref("stock.warehouse0")
        cls.rma_location = cls.wh.rma_loc_id
        cls.stock_location = cls.wh.lot_stock_id

    def setUp(self):
        super().setUp()
        self.product_1.route_ids = self.env["stock.route"].search([])

    def test_1(self):
        wizard = self._rma_sale_wizard(self.sale_order)
        rma = self.env["rma"].browse(wizard.create_and_open_rma()["res_id"])
        self.assertEqual(rma.location_id, self.rma_location)
        self.assertEqual(rma.reception_move_id.location_dest_id, self.rma_location)

    def test_2(self):
        self.operation.return_location_id = self.stock_location
        wizard = self._rma_sale_wizard(self.sale_order)
        rma = self.env["rma"].browse(wizard.create_and_open_rma()["res_id"])
        self.assertEqual(rma.location_id, self.stock_location)
        self.assertEqual(rma.reception_move_id.location_dest_id, self.stock_location)

    def test_3(self):
        stock_return_picking_form = Form(
            self.env["stock.return.picking"].with_context(
                active_ids=self.order_out_picking.ids,
                active_id=self.order_out_picking.id,
                active_model="stock.picking",
            )
        )
        stock_return_picking_form.create_rma = True
        stock_return_picking_form.rma_operation_id = self.operation
        return_wizard = stock_return_picking_form.save()
        return_wizard.create_returns()
        rma = self.order_out_picking.move_ids.rma_ids
        self.assertEqual(rma.location_id, self.rma_location)
        self.assertEqual(rma.reception_move_id.location_dest_id, self.rma_location)

    def test_4(self):
        self.operation.return_location_id = self.stock_location
        stock_return_picking_form = Form(
            self.env["stock.return.picking"].with_context(
                active_ids=self.order_out_picking.ids,
                active_id=self.order_out_picking.id,
                active_model="stock.picking",
            )
        )
        stock_return_picking_form.create_rma = True
        stock_return_picking_form.rma_operation_id = self.operation
        return_wizard = stock_return_picking_form.save()
        self.product_1.route_ids = self.env["stock.route"].search([])
        return_wizard.create_returns()
        rma = self.order_out_picking.move_ids.rma_ids
        self.assertEqual(rma.location_id, self.stock_location)
        self.assertEqual(rma.reception_move_id.location_dest_id, self.stock_location)

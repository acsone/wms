# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import Form

from odoo.addons.rma.tests.test_rma import TestRma


class TestRmaCase(TestRma):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env["product.product"].create(
            {"name": "Product 1", "type": "product"}
        )
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.loc_stock = cls.warehouse.lot_stock_id
        cls.loc_customer = cls.env.ref("stock.stock_location_customers")
        cls.pick_type = cls.env.ref("stock.picking_type_out")
        cls.env["stock.quant"]._update_available_quantity(
            cls.product, cls.loc_stock, 10
        )

    def _create_and_confirm_delivery(self):
        picking_type = self.env["stock.picking.type"].search(
            [
                ("code", "=", "outgoing"),
                "|",
                ("warehouse_id.company_id", "=", self.company.id),
                ("warehouse_id", "=", False),
            ],
            limit=1,
        )
        picking_form = Form(
            recordp=self.env["stock.picking"].with_context(
                default_picking_type_id=picking_type.id
            ),
            view="stock.view_picking_form",
        )
        picking_form.partner_id = self.partner
        with picking_form.move_ids_without_package.new() as move:
            move.product_id = self.product
            move.product_uom_qty = 10
        picking = picking_form.save()
        picking.action_confirm()
        return picking

    def test_0(self):
        """If the delivery picking type is not set to empty package at return, the reception.

        created from the rma have the result package (standard behavior)
        """
        self.pick_type.empty_package_at_return = False
        origin_delivery = self._create_and_confirm_delivery()
        origin_delivery.action_assign()
        origin_delivery.action_set_quantities_to_reservation()
        origin_delivery._put_in_pack(origin_delivery.move_line_ids)
        origin_delivery._action_done()
        stock_return_picking_form = Form(
            self.env["stock.return.picking"].with_context(
                active_ids=origin_delivery.ids,
                active_id=origin_delivery.id,
                active_model="stock.picking",
            )
        )
        stock_return_picking_form.create_rma = True
        stock_return_picking_form.rma_operation_id = self.operation
        return_wizard = stock_return_picking_form.save()
        picking_action = return_wizard.create_returns()
        reception = self.env["stock.picking"].browse(picking_action["res_id"])
        reception_move = reception.move_ids
        self.assertTrue(reception_move.move_line_ids.result_package_id)

    def test_1(self):
        """If the delivery picking type is set to empty package at return, the reception.

        created from the rma have no result package
        """
        self.pick_type.empty_package_at_return = True
        origin_delivery = self._create_and_confirm_delivery()
        origin_delivery.action_assign()
        origin_delivery.action_set_quantities_to_reservation()
        origin_delivery._put_in_pack(origin_delivery.move_line_ids)
        origin_delivery._action_done()
        stock_return_picking_form = Form(
            self.env["stock.return.picking"].with_context(
                active_ids=origin_delivery.ids,
                active_id=origin_delivery.id,
                active_model="stock.picking",
            )
        )
        stock_return_picking_form.create_rma = True
        stock_return_picking_form.rma_operation_id = self.operation
        return_wizard = stock_return_picking_form.save()
        picking_action = return_wizard.create_returns()
        reception = self.env["stock.picking"].browse(picking_action["res_id"])
        reception_move = reception.move_ids
        self.assertFalse(reception_move.move_line_ids.result_package_id)

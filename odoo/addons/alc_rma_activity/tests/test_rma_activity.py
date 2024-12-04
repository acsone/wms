# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import Form

from odoo.addons.rma.tests.test_rma import TestRma


class TestRmaActivity(TestRma):
    def test_receive(self):
        self.operation.create_inventory_activity_reception = True
        rma = self._create_rma(self.partner, self.product, 10, self.rma_loc)
        rma.action_confirm()
        rma.reception_move_id.quantity_done = 10
        rma.reception_move_id.picking_id._action_done()
        activity = self.env["mail.activity"].search(
            [
                ("res_model_id", "=", self.env["ir.model"]._get("rma").id),
                ("res_id", "=", rma.id),
                ("summary", "=", "Inventory actions required after reception"),
            ]
        )
        self.assertEqual(len(activity), 1, "Activity was not created after reception.")

    def test_replace(self):
        self.operation.create_inventory_activity_delivery = True
        rma = self._create_confirm_receive(self.partner, self.product, 10, self.rma_loc)
        product_2 = self.product_product.create(
            {"name": "Product 2 test", "type": "product"}
        )
        delivery_form = Form(
            self.env["rma.delivery.wizard"].with_context(
                active_ids=rma.ids,
                rma_delivery_type="replace",
            )
        )
        delivery_form.product_id = product_2
        delivery_form.product_uom_qty = 2
        delivery_wizard = delivery_form.save()
        delivery_wizard.action_deliver()
        picking = rma.delivery_move_ids.picking_id
        picking.move_ids.quantity_done = 8
        picking.button_validate()
        activity = self.env["mail.activity"].search(
            [
                ("res_model_id", "=", self.env["ir.model"]._get("rma").id),
                ("res_id", "=", rma.id),
                ("summary", "=", "Inventory actions required after delivery"),
            ]
        )
        self.assertEqual(len(activity), 1, "Activity was not created after reception.")

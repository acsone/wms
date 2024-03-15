# Copyright 2021 ACSONE SA/NV.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import ValidationError
from odoo.tests import Form

from odoo.addons.delivery_carrier_label_gls.tests.common import mock_gls_client

from .common import TestGLSWizard


class TestGlsFlow(TestGLSWizard):
    def test_button_put_in_pack(self):
        wizard_model = self.env["delivery.package.gls.wizard"]
        self.sale_order.action_confirm()
        picking = self.sale_order.picking_ids
        # Activate the GLS wizard
        picking.picking_type_id.show_gls_put_in_pack_wizard = True
        picking.action_assign()

        move_line_1 = picking.move_line_ids[0]
        move_line_2 = picking.move_line_ids[1]

        move_line_1.qty_done = move_line_1.reserved_uom_qty
        gls_wizard_action_1 = picking.action_put_in_pack()

        # Check if the returned wizard is GLS one
        self.assertEqual(
            gls_wizard_action_1.get("res_model"), "delivery.package.gls.wizard"
        )
        # This simulates the action return and the wizard creation
        # triggering computes and onchanges
        wizard_1 = Form(wizard_model.with_context(**gls_wizard_action_1["context"]))
        gls_wizard_1 = wizard_1.save()
        gls_wizard_1.shipping_weight = self.product.weight
        with mock_gls_client():
            gls_wizard_1.put_in_pack()
        package_1 = gls_wizard_1.package_id
        self.assertEqual(package_1.shipping_weight, self.product.weight)

        move_line_2.qty_done = move_line_2.reserved_uom_qty
        gls_wizard_action_2 = picking.action_put_in_pack()
        wizard_2 = Form(wizard_model.with_context(**gls_wizard_action_2["context"]))
        gls_wizard_2 = wizard_2.save()
        gls_wizard_2.shipping_weight = self.product_1.weight
        with mock_gls_client():
            gls_wizard_2.put_in_pack()
        package_2 = gls_wizard_2.package_id
        self.assertEqual(package_2.shipping_weight, self.product_1.weight)
        self.assertFalse(picking.can_put_in_pack)

    def test_do_transfer(self):
        wizard_model = self.env["delivery.package.gls.wizard"]
        self.sale_order.action_confirm()
        picking = self.sale_order.picking_ids
        picking.action_assign()

        for move_line in picking.move_line_ids:
            move_line.qty_done = move_line.reserved_uom_qty
        package_id = picking._put_in_pack(picking.move_line_ids).id

        # so now, when we validate the picking we get a wizard back:
        gls_wizard_transfer_action = picking.button_validate()
        wizard = Form(
            wizard_model.with_context(**gls_wizard_transfer_action["context"])
        )
        gls_wizard_transfer = wizard.save()
        self.assertEqual(gls_wizard_transfer.package_id.id, package_id)
        self.assertEqual(gls_wizard_transfer.allowed_package_ids.ids, [package_id])

    def test_unreserve_moves(self):
        wizard_model = self.env["delivery.package.gls.wizard"]
        self.sale_order.action_confirm()
        picking = self.sale_order.picking_ids
        picking.action_assign()
        move_line_1 = picking.move_line_ids[0]
        move_line_1.qty_done = move_line_1.reserved_uom_qty

        gls_wizard_action_1 = picking.action_put_in_pack()
        wizard = Form(wizard_model.with_context(**gls_wizard_action_1["context"]))
        gls_wizard_1 = wizard.save()
        gls_wizard_1.shipping_weight = self.product.weight
        with mock_gls_client():
            gls_wizard_1.put_in_pack()

        with self.assertRaises(ValidationError), self.env.cr.savepoint():
            picking.do_unreserve()

        with mock_gls_client():
            gls_wizard_1.abort()
        picking.do_unreserve()
        self.assertEqual(0, picking.move_line_ids.reserved_uom_qty)

# Copyright 2021 ACSONE SA/NV.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import ValidationError

from odoo.addons.delivery_carrier_label_gls.tests.common import mock_gls_client

from .common import TestGLSWizard


class TestGlsFlow(TestGLSWizard):
    def test_button_put_in_pack(self):
        wizard_model = self.env["delivery.package.gls.wizard"]
        self.sale_order.action_confirm()
        picking = self.sale_order.picking_ids
        picking.action_assign()

        move_line_1 = picking.move_line_ids[0]
        move_line_2 = picking.move_line_ids[1]

        move_line_1.qty_done = move_line_1.reserved_uom_qty
        gls_wizard_action_1 = picking.button_gls_put_in_pack()
        gls_wizard_1 = wizard_model.browse(gls_wizard_action_1["res_id"])
        gls_wizard_1.shipping_weight = self.product.weight
        with mock_gls_client():
            gls_wizard_1.put_in_pack()
        package_1 = gls_wizard_1.package_id
        self.assertEqual(package_1.shipping_weight, self.product.weight)

        move_line_2.qty_done = move_line_2.reserved_uom_qty
        gls_wizard_action_2 = picking.button_gls_put_in_pack()
        gls_wizard_2 = wizard_model.browse(gls_wizard_action_2["res_id"])
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

        move_line_1 = picking.move_line_ids[0]
        move_line_1.qty_done = move_line_1.reserved_uom_qty
        package_id = picking._put_in_pack(move_line_1).id

        # so now, when we validate the picking we get a wizard back:
        gls_wizard_transfer_action = picking.button_validate()
        gls_wizard_transfer = wizard_model.browse(gls_wizard_transfer_action["res_id"])

        self.assertEqual(gls_wizard_transfer.package_id.id, package_id)

    def test_unreserve_moves(self):
        wizard_model = self.env["delivery.package.gls.wizard"]
        self.sale_order.action_confirm()
        picking = self.sale_order.picking_ids
        picking.action_assign()
        move_line_1 = picking.move_line_ids[0]
        move_line_1.qty_done = move_line_1.reserved_uom_qty
        gls_wizard_action_1 = picking.button_gls_put_in_pack()
        gls_wizard_1 = wizard_model.browse(gls_wizard_action_1["res_id"])
        gls_wizard_1.shipping_weight = self.product.weight
        with mock_gls_client():
            gls_wizard_1.put_in_pack()

        with self.assertRaises(ValidationError), self.env.cr.savepoint():
            picking.do_unreserve()

        with mock_gls_client():
            gls_wizard_1.abort()
        picking.do_unreserve()
        self.assertEqual(0, picking.move_line_ids.reserved_uom_qty)

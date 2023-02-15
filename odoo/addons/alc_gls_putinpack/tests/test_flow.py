# coding: utf-8
# Copyright 2021 ACSONE SA/NV.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

# import mock

from odoo.exceptions import ValidationError

from odoo.addons.delivery_carrier_label_gls.tests.common import mock_gls_client

from .common import TestGLSWizard


class MockGlsClientRaise(object):
    def create_parcel(self, shipment_payload):
        raise ValidationError


class TestGlsFlow(TestGLSWizard):
    def test_button_put_in_pack(self):
        wizard_model = self.env["delivery.package.gls.wizard"]
        self.sale_order.action_confirm()
        picking = self.sale_order.picking_ids
        picking.force_assign()

        pack_operation_1 = picking.pack_operation_ids[0]
        pack_operation_2 = picking.pack_operation_ids[1]

        pack_operation_1.qty_done = pack_operation_1.product_qty
        gls_wizard_action_1 = picking.button_gls_put_in_pack()
        gls_wizard_1 = wizard_model.browse(gls_wizard_action_1["res_id"])
        gls_wizard_1.shipping_weight = self.product.weight
        with mock_gls_client():
            gls_wizard_1.put_in_pack()
        package_1 = gls_wizard_1.package_id
        self.assertEqual(package_1.shipping_weight, self.product.weight)

        pack_operation_2.qty_done = pack_operation_2.product_qty
        gls_wizard_action_2 = picking.button_gls_put_in_pack()
        gls_wizard_2 = wizard_model.browse(gls_wizard_action_2["res_id"])
        gls_wizard_2.shipping_weight = self.product_2.weight
        with mock_gls_client():
            gls_wizard_2.put_in_pack()
        package_2 = gls_wizard_2.package_id
        self.assertEqual(package_2.shipping_weight, self.product_2.weight)
        self.assertFalse(picking.can_put_in_pack)

        # after_rollback doesn't work in test mode :-/
        # mock_client_raise = MockGlsClientRaise()
        # with self.mock_gls_client(mock_client_raise):
        #     with self.assertRaises(ValidationError):
        #         gls_wizard_1.send()
        #
        # # then: we still updated the package!
        # self.assertEqual(package_1.shipping_weight, shipping_weight)
        # self.assertEqual(package_1.packaging_id, packaging_parcel)
        # self.assertFalse(package_1.parcel_tracking)

    def test_do_transfer(self):
        wizard_model = self.env["delivery.package.gls.wizard"]
        self.sale_order.action_confirm()
        picking = self.sale_order.picking_ids
        picking.force_assign()

        pack_operation_1 = picking.pack_operation_ids[0]
        pack_operation_1.qty_done = pack_operation_1.product_qty
        package_id = picking.put_in_pack()["res_id"]  # we get the view back

        # so now, when we validate the picking we get a wizard back:
        gls_wizard_transfer_action = picking.do_transfer()
        gls_wizard_transfer = wizard_model.browse(gls_wizard_transfer_action["res_id"])

        self.assertEqual(gls_wizard_transfer.package_id.id, package_id)

    def test_unreserve_moves(self):
        wizard_model = self.env["delivery.package.gls.wizard"]
        self.sale_order.action_confirm()
        picking = self.sale_order.picking_ids
        picking.force_assign()
        pack_operation_1 = picking.pack_operation_ids[0]
        pack_operation_1.qty_done = pack_operation_1.product_qty
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
        self.assertFalse(picking.pack_operation_ids)

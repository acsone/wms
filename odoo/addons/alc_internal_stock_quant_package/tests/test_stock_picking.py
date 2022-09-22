# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError

from .common import TestStockPickingInternal


class TestStockPickingInternalFlow(TestStockPickingInternal):
    def test_internal_result_package_emptied_on_transfer(self):
        self.assertEqual(self.picking.state, "assigned")
        packop = self.picking.pack_operation_ids
        packop.write(
            dict(
                result_package_id=self.internal_package.id, qty_done=packop.product_qty,
            )
        )
        self.picking.do_new_transfer()
        self.assertEqual(self.picking.state, "done")
        self.assertFalse(self.internal_package.quant_ids)

    def test_internal_package_emptied_on_transfer(self):
        self.assertEqual(self.picking.state, "assigned")
        # create a pack operation on package
        self.internal_package.quant_ids = self.picking.move_lines.reserved_quant_ids
        self.picking.do_unreserve()
        self.picking.action_assign()

        packop = self.picking.pack_operation_ids
        self.assertEqual(self.internal_package, packop.package_id)
        packop.qty_done = packop.product_qty
        self.picking.do_new_transfer()
        self.assertEqual(self.picking.state, "done")
        self.assertFalse(self.internal_package.quant_ids)

    def test_internal_package_not_emptied_on_transfer(self):
        self.picking_type_out.empty_internal_package_on_transfer = False
        self.assertEqual(self.picking.state, "assigned")
        # create a pack operation on package
        self.internal_package.quant_ids = self.picking.move_lines.reserved_quant_ids
        self.picking.do_unreserve()
        self.picking.action_assign()

        packop = self.picking.pack_operation_ids
        self.assertEqual(self.internal_package, packop.package_id)
        packop.qty_done = packop.product_qty
        self.picking.do_new_transfer()
        self.assertEqual(self.picking.state, "done")
        self.assertTrue(self.internal_package.quant_ids)

    def test_internal_result_package_not_emptied_on_transfer(self):
        self.picking_type_out.empty_internal_package_on_transfer = False
        self.assertEqual(self.picking.state, "assigned")
        packop = self.picking.pack_operation_ids
        packop.write(
            dict(
                result_package_id=self.internal_package.id, qty_done=packop.product_qty,
            )
        )
        self.picking.do_new_transfer()
        self.assertEqual(self.picking.state, "done")
        self.assertTrue(self.internal_package.quant_ids)

    def test_external_package_not_emptied_on_transfer(self):
        self.assertEqual(self.picking.state, "assigned")
        packop = self.picking.pack_operation_ids
        packop.write(
            dict(
                result_package_id=self.external_package.id, qty_done=packop.product_qty,
            )
        )
        self.picking.do_new_transfer()
        self.assertEqual(self.picking.state, "done")
        self.assertTrue(self.external_package.quant_ids)

    def test_internal_package_emptied_on_put_in_pack(self):
        self.assertEqual(self.picking.state, "assigned")
        packop = self.picking.pack_operation_ids
        packop.write(
            dict(
                result_package_id=self.internal_package.id, qty_done=packop.product_qty,
            )
        )
        self.picking.put_in_pack()
        self.assertNotEqual(packop.result_package_id, self.internal_package)
        self.picking.do_new_transfer()
        self.assertEqual(self.picking.state, "done")
        self.assertFalse(self.internal_package.quant_ids)

    def test_internal_package_not_emptied_on_put_in_pack(self):
        self.picking_type_out.empty_internal_package_on_transfer = False
        self.assertEqual(self.picking.state, "assigned")
        packop = self.picking.pack_operation_ids
        packop.write(
            dict(
                result_package_id=self.internal_package.id, qty_done=packop.product_qty,
            )
        )
        with self.assertRaisesRegexp(
            UserError, "Please process some quantities to put in the pack first!",
        ), self.env.cr.savepoint():
            self.picking.put_in_pack()
        self.equal = self.assertEqual(packop.result_package_id, self.internal_package)
        self.picking.do_new_transfer()
        self.assertEqual(self.picking.state, "done")
        self.assertTrue(self.internal_package.quant_ids)

    def test_internal_package_emptied_on_transfer_depend_on_carrier(self):
        carrier_1 = self.env["delivery.carrier"].create({"name": "Carrier1"})
        self.picking.carrier_id = carrier_1
        vals_line = {"empty": False, "delivery_carrier_id": carrier_1.id}
        vals = {"stock_internal_package_config_line_ids": [(0, 0, vals_line)]}
        self.picking_type_out.write(vals)

        self.assertFalse(self.picking.empty_internal_package_on_transfer)

        line = self.picking_type_out.stock_internal_package_config_line_ids
        line.empty = True

        self.assertTrue(self.picking.empty_internal_package_on_transfer)

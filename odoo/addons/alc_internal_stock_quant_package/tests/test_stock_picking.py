# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError
from odoo.tests.common import SavepointCase


class TestStockPicking(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestStockPicking, cls).setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context, tracking_disable=True, test_queue_job_no_delay=True,
            )
        )
        cls.picking_type_out = cls.env.ref("stock.picking_type_out")
        cls.internal_package = cls.env["stock.quant.package"].create(
            {"is_internal": True}
        )
        cls.external_package = cls.env["stock.quant.package"].create({})
        cls.product_a = cls.env["product.product"].create(
            {"name": "Product A", "type": "product"}
        )
        cls.customer_location = cls.env.ref("stock.stock_location_customers")
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.picking = cls.env["stock.picking"].create(
            {
                "picking_type_id": cls.picking_type_out.id,
                "location_dest_id": cls.customer_location.id,
                "location_id": cls.stock_location.id,
            }
        )
        cls.env["stock.move"].create(
            {
                "name": cls.product_a.name,
                "product_id": cls.product_a.id,
                "product_uom_qty": 1,
                "product_uom": cls.product_a.uom_id.id,
                "picking_id": cls.picking.id,
                "location_dest_id": cls.customer_location.id,
                "location_id": cls.stock_location.id,
            }
        )
        wiz = cls.env["stock.change.product.qty"].create(
            {
                "product_id": cls.product_a.id,
                "product_tmpl_id": cls.product_a.product_tmpl_id.id,
                "new_quantity": 1,
                "location_id": cls.stock_location.id,
            }
        )
        wiz.change_product_qty()

        cls.picking.action_assign()

    def test_internal_result_package_emptied_on_transfer(self):
        self.assertTrue(self.picking_type_out.empty_internal_package_on_transfer)
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
        self.assertTrue(self.picking_type_out.empty_internal_package_on_transfer)
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
        self.assertTrue(self.picking_type_out.empty_internal_package_on_transfer)
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
        self.assertTrue(self.picking_type_out.empty_internal_package_on_transfer)
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
        self.assertTrue(self.picking_type_out.empty_internal_package_on_transfer)
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
        self.assertTrue(self.picking_type_out.empty_internal_package_on_transfer)
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
        self.assertTrue(self.picking_type_out.empty_internal_package_on_transfer)
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

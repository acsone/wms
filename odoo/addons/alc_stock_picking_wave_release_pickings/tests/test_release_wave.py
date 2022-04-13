# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError
from odoo.tests.common import SavepointCase


class TestReleaseWave(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestReleaseWave, cls).setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.parameter_model = cls.env["ir.config_parameter"]
        cls.parameter_model.sudo().set_param(
            "constrain_release_picking_wave_before_unlink", "1"
        )
        cls.warehouse_1 = cls.env.ref("stock.warehouse0")
        cls.customer = cls.env["res.partner"].create({"name": "Customer"})
        cls.product_1 = cls.env["product.product"].create(
            {
                "name": "Product A",
                "type": "product",
                "default_code": "A",
                "barcode": "A",
                "weight": 2,
            }
        )
        cls.product_2 = cls.env["product.product"].create(
            {
                "name": "Product B",
                "type": "product",
                "default_code": "B",
                "barcode": "B",
                "weight": 3,
            }
        )
        cls.pick1 = cls._create_picking()
        cls.pick2 = cls._create_picking()
        cls.pick3 = cls._create_picking()
        picking_ids = [cls.pick1.id, cls.pick2.id, cls.pick3.id]
        cls.batch = cls._create_batch(picking_ids)

        cls.operator = cls.env["res.users"].browse(cls.env.uid)

    @classmethod
    def _create_picking(cls, lines=None):
        warehouse = cls.warehouse_1
        Picking = cls.env["stock.picking"]
        move_lines = []
        picking_values = {
            "partner_id": cls.customer.id,
            "move_lines": move_lines,
            "picking_type_id": warehouse.pick_type_id.id,
            "location_id": cls.env.ref("stock.stock_location_stock").id,
            "location_dest_id": warehouse.wh_output_stock_loc_id.id,
        }
        if lines is None:
            lines = [(cls.product_1, 10), (cls.product_2, 10)]
        for product, qty in lines:
            move_lines.append(
                (
                    0,
                    0,
                    {
                        "name": product.name,
                        "product_id": product.id,
                        "product_uom_qty": qty,
                        "product_uom": product.uom_id.id,
                        "location_id": cls.env.ref("stock.stock_location_stock").id,
                        "location_dest_id": warehouse.wh_output_stock_loc_id.id,
                    },
                )
            )
        picking = Picking.create(picking_values)
        return picking

    @classmethod
    def _create_batch(cls, picking_ids):
        batch = cls.env["stock.picking.wave"].create(
            {"picking_ids": [(6, None, picking_ids)]}
        )
        return batch

    def test_00_create_batch_draft_release(self):
        self.assertEqual(self.batch.state, "draft")
        self.assertEqual(self.pick1.wave_id, self.batch)
        self.assertEqual(self.pick2.wave_id, self.batch)
        self.assertEqual(self.pick3.wave_id, self.batch)

        self.batch.release()
        self.assertEqual(self.batch.state, "released")
        self.assertFalse(self.pick1.wave_id)
        self.assertFalse(self.pick2.wave_id)
        self.assertFalse(self.pick3.wave_id)

    def test_01_create_batch_start_release(self):
        """
        Batch is in progress (operator is assigned etc)
        but no picking is started yet : it is possible to release the pickings
        """
        self.batch.picking_ids.action_confirm()
        self.batch.picking_ids.action_assign()
        self.batch.write(
            {"state": "in_progress", "printed": True, "operator_id": self.env.uid}
        )

        self.assertEqual(self.pick1.wave_id, self.batch)
        self.assertEqual(self.pick2.wave_id, self.batch)
        self.assertEqual(self.pick3.wave_id, self.batch)
        self.assertTrue(self.pick1.printed)
        self.assertTrue(self.pick2.printed)
        self.assertTrue(self.pick3.printed)
        self.assertEqual(self.pick1.operator_id, self.operator)
        self.assertEqual(self.pick2.operator_id, self.operator)
        self.assertEqual(self.pick3.operator_id, self.operator)

        self.batch.release()
        self.assertEqual(self.batch.state, "released")
        self.assertFalse(self.pick1.wave_id)
        self.assertFalse(self.pick2.wave_id)
        self.assertFalse(self.pick3.wave_id)
        self.assertFalse(self.pick1.printed)
        self.assertFalse(self.pick2.printed)
        self.assertFalse(self.pick3.printed)

    def test_02_create_batch_started_no_release(self):
        """
        Batch is in progress (operator is assigned etc)
        and one picking is started : impossible to release the pickings
        """
        self.batch.picking_ids.action_confirm()
        self.batch.picking_ids.action_assign()
        self.batch.picking_ids.force_assign()
        self.batch.write(
            {"state": "in_progress", "printed": True, "operator_id": self.env.uid}
        )

        for pack in self.pick1.pack_operation_ids:
            pack.qty_done = pack.product_qty
        self.assertEqual(self.pick1.wave_id, self.batch)
        self.assertEqual(self.pick2.wave_id, self.batch)
        self.assertEqual(self.pick3.wave_id, self.batch)
        self.assertTrue(self.pick1.printed)
        self.assertTrue(self.pick2.printed)
        self.assertTrue(self.pick3.printed)
        self.assertEqual(self.pick1.operator_id, self.operator)
        self.assertEqual(self.pick2.operator_id, self.operator)
        self.assertEqual(self.pick3.operator_id, self.operator)

        with self.assertRaises(ValidationError):
            self.batch.release()

    def test_03_unlink_canceled_wave(self):
        """
        Try to delete wave that is already canceled : it's ok
        """
        self.batch.picking_ids.action_confirm()
        self.batch.picking_ids.action_assign()
        self.batch.with_context(force_cancel=True).cancel_picking()

        self.assertEqual(self.batch.state, "cancel")
        self.assertEqual(self.pick1.state, "cancel")
        self.assertEqual(self.pick2.state, "cancel")
        self.assertEqual(self.pick3.state, "cancel")

        self.batch.unlink()

    def test_04_unlink_released_wave(self):
        """
        Try to delete wave that is already released : it's ok
        """
        self.batch.picking_ids.action_confirm()
        self.batch.picking_ids.action_assign()
        self.batch.release()

        self.assertEqual(self.batch.state, "released")
        self.assertEqual(self.pick1.state, "confirmed")
        self.assertEqual(self.pick2.state, "confirmed")
        self.assertEqual(self.pick3.state, "confirmed")

        self.batch.unlink()

    def test_05_unlink_draft_wave(self):
        """
        Try to delete wave that is in draft state : it's not ok
        """
        self.assertEqual(self.batch.state, "draft")
        self.assertEqual(self.pick1.state, "draft")
        self.assertEqual(self.pick2.state, "draft")
        self.assertEqual(self.pick3.state, "draft")

        with self.assertRaises(ValidationError):
            self.batch.unlink()

    def test_06_unlink_confirmed_wave(self):
        """
        Try to delete wave that is in draft state : it's not ok
        """
        self.batch.picking_ids.action_confirm()
        self.batch.picking_ids.action_assign()
        self.batch.write({"state": "in_progress"})
        self.assertEqual(self.batch.state, "in_progress")
        self.assertEqual(self.pick1.state, "confirmed")
        self.assertEqual(self.pick2.state, "confirmed")
        self.assertEqual(self.pick3.state, "confirmed")

        with self.assertRaises(ValidationError):
            self.batch.unlink()

    def test_07_create_batch_start_releaserelease_already_released(self):
        """
        Batch has already been released and we try to release it again : not allowed
        """
        self.batch.picking_ids.action_confirm()
        self.batch.picking_ids.action_assign()
        self.batch.release()
        self.assertEqual(self.batch.state, "released")
        self.assertTrue(self.batch.release_not_allowed)
        with self.assertRaises(ValidationError):
            self.batch.release()

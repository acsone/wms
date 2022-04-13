# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError

from odoo.addons.alc_shopfloor.tests.test_cluster_picking_base import (
    ClusterPickingCommonCase,
)


class TestUnassignWave(ClusterPickingCommonCase):
    @classmethod
    def setUpClass(cls):
        super(TestUnassignWave, cls).setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.parameter_model = cls.env["ir.config_parameter"]
        cls.parameter_model.sudo().set_param(
            "constrain_release_picking_wave_before_unlink", "1"
        )
        cls.batch = cls._create_picking_batch(
            [
                [
                    cls.BatchProduct(product=cls.product_a, quantity=10),
                    cls.BatchProduct(product=cls.product_b, quantity=10),
                ],
                [cls.BatchProduct(product=cls.product_a, quantity=10)],
            ]
        )

    def test_00_create_batch_start_unassign(self):
        response = self.service.dispatch(
            "unassign", params={"picking_batch_id": self.batch.id}
        )

        expected = {"data": {"start": {}}, "next_state": "start"}
        self.assertEqual(response, expected)

    def test_01_started_batch_cannot_unassign(self):

        self.bin1 = self.env["stock.quant.package"].create({})
        self._simulate_batch_selected(self.batch)
        operation = self.batch.pack_operation_ids[0]
        qty_done = operation.product_qty
        # process one operation
        self.service.dispatch(
            "scan_destination_pack",
            params={
                "picking_batch_id": self.batch.id,
                "operation_id": operation.id,
                "barcode": self.bin1.name,
                "quantity": qty_done,
            },
        )
        self.assertTrue(
            any(self.batch.mapped("picking_ids.pack_operation_ids.qty_done"))
        )
        # try to cancel batch -- should not be possible since one picking is started
        with self.assertRaises(ValidationError), self.env.cr.savepoint():
            self.service.dispatch(
                "unassign", params={"picking_batch_id": self.batch.id},
            )

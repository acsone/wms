# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import mock

from odoo.addons.alc_shopfloor.tests.test_cluster_picking_base import (
    ClusterPickingCommonCase,
)


# pylint: disable=missing-return
class TestClusterPickingFindBatch(ClusterPickingCommonCase):
    @classmethod
    def setUpClassBaseData(cls, *args, **kwargs):
        super(TestClusterPickingFindBatch, cls).setUpClassBaseData(*args, **kwargs)
        # drop base demo data and create our own batches to work with
        cls.env["stock.picking.wave"].search([]).unlink()
        cls.device1 = cls._create_device("device1", 10, 50, 100, 6, 50)
        weight = 10
        length = 10
        height = 1
        width = 1
        volume = length * height * width
        cls.product_a.write(
            {
                "weight": weight,
                "length": length,
                "height": height,
                "width": width,
                "volume": volume,
            }
        )
        cls.menu.sudo().stock_device_type_ids = cls.device1
        cls.menu.sudo().batch_create = True

    def setUp(self):
        super(TestClusterPickingFindBatch, self).setUp()
        # Avoid to have to create a delivery round for our simple tests
        MakePickingBatch = self.env["make.picking.batch"].__class__
        get_delivery_round_patcher = mock.patch.object(
            MakePickingBatch, "_get_delivery_rounds"
        )
        self.mocked_get_delivery_round = get_delivery_round_patcher.start()
        self.mocked_get_delivery_round.return_value = None

        # pylint: disable=unused-variable
        @self.addCleanup
        def stop_mock():
            get_delivery_round_patcher.stop()

    @classmethod
    def _create_device(
        cls, name, min_volume, max_volume, max_weight, nbr_bins, sequence
    ):
        return cls.env["stock.device.type"].create(
            {
                "name": name,
                "min_volume_liter": min_volume * 1000,
                "max_volume_liter": max_volume * 1000,
                "max_weight": max_weight,
                "nbr_bins": nbr_bins,
                "sequence": sequence,
            }
        )

    def _create_sample_picking(self):
        self.picking_id = self._create_picking(lines=[(self.product_a, 3)])
        self._fill_stock_for_moves(self.picking_id.mapped("move_lines"))
        self.picking_id.action_confirm()
        self.picking_id.action_assign()

    def test_find_batch_create_no_batch(self):
        """If no batch found create try to create a new batch
        If not picking to batch -> nothing to do
        """
        # Simulate the client asking a batch by clicking on "get work"
        response = self.service.dispatch("find_batch")
        self.assert_response(
            response,
            next_state="start",
            message={
                "message_type": "info",
                "body": "No more work to do, please create a new batch transfer",
            },
        )

    def test_find_batch_create_batch(self):
        """If no batch found create try to create a new batch
        If picking to batch -> get new batch
        """
        self._create_sample_picking()
        response = self.service.dispatch("find_batch")
        data = self.data.picking_batch(self.picking_id.batch_id, with_pickings=True)
        self.assert_response(
            response, next_state="confirm_start", data=data,
        )
        self.assertEqual(self.picking_id.operator_id, self.shopfloor_user)
        self.assertTrue(self.picking_id.printed)
        batch = self.env["stock.picking.wave"].browse(data["id"])
        self.assertEqual(batch.operator_id, self.shopfloor_user)
        self.assertTrue(batch.printed)
        self.assertEqual(batch.state, "in_progress")

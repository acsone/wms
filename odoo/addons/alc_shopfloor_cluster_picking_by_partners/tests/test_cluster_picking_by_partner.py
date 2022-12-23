# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import mock

from odoo.addons.alc_shopfloor.tests.test_cluster_picking_base import (
    ClusterPickingCommonCase,
)


class TestClusterPickingByPartner(ClusterPickingCommonCase):
    @classmethod
    def setUpClass(cls):
        super(TestClusterPickingByPartner, cls).setUpClass()
        cls.env["stock.picking.wave"].search([]).unlink()
        cls.device1 = cls._create_device("device1", 0, 300, 300, 8, 50)
        cls.product_a.write(
            {"weight": 1, "length": 1, "height": 2, "width": 1, "volume": 2}
        )

        cls.menu.sudo().write(
            {
                "batch_create": True,
                "group_pickings_by_partner": True,
                "stock_device_type_ids": [(4, cls.device1.id)],
            }
        )

        cls.bin1 = cls.env["stock.quant.package"].create(
            {"name": "bin1", "is_internal": True}
        )
        cls.bin2 = cls.env["stock.quant.package"].create(
            {"name": "bin2", "is_internal": True}
        )

        cls.customer1 = (
            cls.env["res.partner"]
            .sudo()
            .create({"name": "customer1 for vet", "ref": "12345876"})
        )
        cls.customer2 = (
            cls.env["res.partner"]
            .sudo()
            .create({"name": "customer2 for vet", "ref": "1234222876"})
        )
        cls.picking = cls._create_picking(lines=[(cls.product_a, 3)])
        cls.picking.picking_type_id = cls.picking_type.id

        cls._fill_stock_for_moves(cls.picking.mapped("move_lines"))
        cls.picking.action_confirm()
        cls.picking.action_assign()
        cls.picking1 = cls._create_picking(lines=[(cls.product_b, 1)])
        cls.picking1.picking_type_id = cls.picking_type.id
        cls._fill_stock_for_moves(cls.picking1.mapped("move_lines"))
        cls.picking1.action_confirm()
        cls.picking1.action_assign()

    def setUp(self):
        super(TestClusterPickingByPartner, self).setUp()
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

    def test_create_batch(self):
        response = self.service.dispatch("find_batch")
        data = self.data.picking_batch(self.picking.batch_id, with_pickings=True)
        self.assert_response(
            response, next_state="confirm_start", data=data,
        )
        batch = self.env["stock.picking.wave"].browse(data["id"])
        self.assertEqual(batch.operator_id, self.shopfloor_user)
        self.assertTrue(batch.printed)
        self.assertEqual(batch.state, "in_progress")
        self.assertEqual(batch.wave_nbr_bins, 1)

    def test_several_customer_in_one_bin_and_unload_all(self):
        self.picking.customer_id = self.customer1.id
        self.picking1.customer_id = self.customer2.id
        line1 = self.picking.pack_operation_ids[0]
        line2 = self.picking1.pack_operation_ids[0]
        response = self.service.dispatch("find_batch")
        data = self.data.picking_batch(self.picking.batch_id, with_pickings=True)
        self.assert_response(
            response, next_state="confirm_start", data=data,
        )
        batch = self.picking.batch_id
        response = self.service.dispatch(
            "scan_line",
            params={
                "picking_batch_id": batch.id,
                "operation_id": line1.id,
                "barcode": line1.product_id.barcode,
            },
        )
        self.assert_response(
            response, next_state="scan_destination", data=self._operation_data(line1)
        )
        qty_done1 = line1.product_qty
        response = self.service.dispatch(
            "scan_destination_pack",
            params={
                "picking_batch_id": batch.id,
                "operation_id": line1.id,
                "barcode": self.bin1.name,
                "quantity": qty_done1,
            },
        )
        self.assertRecordValues(
            line1, [{"qty_done": qty_done1, "result_package_id": self.bin1.id}]
        )
        self.assert_response(
            response,
            next_state="start_operation",
            data=self._operation_data(line2),
            message={
                "message_type": "success",
                "body": "{} {} put in {}".format(
                    line1.qty_done, line1.product_id.display_name, self.bin1.name,
                ),
            },
        )
        qty_done2 = line2.product_qty
        response = self.service.dispatch(
            "scan_destination_pack",
            params={
                "picking_batch_id": batch.id,
                "operation_id": line2.id,
                "barcode": self.bin1.name,
                "quantity": qty_done2,
            },
        )
        self.assertRecordValues(
            line2, [{"qty_done": qty_done2, "result_package_id": self.bin1.id}]
        )
        operations = batch.picking_ids.mapped("pack_operation_ids")
        operations.write({"location_dest_id": self.packing_location.id})
        response = self.service.dispatch(
            "set_destination_all",
            params={
                "picking_batch_id": batch.id,
                "barcode": self.packing_location.barcode,
            },
        )
        # since the whole batch is complete, we expect the batch and all
        # pickings to be 'done'
        self.assertRecordValues(
            operations.mapped("picking_id"), [{"state": "done"}, {"state": "done"}]
        )
        self.assertRecordValues(
            operations,
            [
                {
                    "shopfloor_unloaded": True,
                    "qty_done": qty_done1,
                    "state": "done",
                    "location_dest_id": self.packing_location.id,
                },
                {
                    "shopfloor_unloaded": True,
                    "qty_done": qty_done2,
                    "state": "done",
                    "location_dest_id": self.packing_location.id,
                },
            ],
        )
        self.assertRecordValues(batch, [{"state": "done"}])
        self.assert_response(
            response,
            next_state="start",
            message={"message_type": "success", "body": "Batch Transfer complete"},
        )

    def test_several_partner_in_one_bin(self):
        self.picking.partner_id = self.customer1.id
        self.picking1.partner_id = self.customer2.id
        line1 = self.picking.pack_operation_ids[0]
        line2 = self.picking1.pack_operation_ids[0]
        response = self.service.dispatch("find_batch")
        data = self.data.picking_batch(self.picking.batch_id, with_pickings=True)
        self.assert_response(
            response, next_state="confirm_start", data=data,
        )
        batch = self.picking.batch_id
        response = self.service.dispatch(
            "scan_line",
            params={
                "picking_batch_id": batch.id,
                "operation_id": line1.id,
                "barcode": line1.product_id.barcode,
            },
        )
        self.assert_response(
            response, next_state="scan_destination", data=self._operation_data(line1)
        )
        qty_done1 = line1.product_qty
        response = self.service.dispatch(
            "scan_destination_pack",
            params={
                "picking_batch_id": batch.id,
                "operation_id": line1.id,
                "barcode": self.bin1.name,
                "quantity": qty_done1,
            },
        )
        self.assertRecordValues(
            line1, [{"qty_done": qty_done1, "result_package_id": self.bin1.id}]
        )
        self.assert_response(
            response,
            next_state="start_operation",
            data=self._operation_data(line2),
            message={
                "message_type": "success",
                "body": "{} {} put in {}".format(
                    line1.qty_done, line1.product_id.display_name, self.bin1.name,
                ),
            },
        )
        qty_done2 = line2.product_qty
        response = self.service.dispatch(
            "scan_destination_pack",
            params={
                "picking_batch_id": batch.id,
                "operation_id": line2.id,
                "barcode": self.bin1.name,
                "quantity": qty_done2,
            },
        )

        self.assert_response(
            response,
            next_state="scan_destination",
            data=self._operation_data(line2),
            message={
                "message_type": "error",
                "body": "The destination bin {} is not empty,"
                " please take another.".format(self.bin1.name),
            },
        )

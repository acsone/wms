# -*- coding: utf-8 -*-
# Copyright 2020 Camptocamp SA (http://www.camptocamp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import unittest

from .test_cluster_picking_base import ClusterPickingCommonCase


# pylint: disable=missing-return
class ClusterPickingChangePackLotCase(ClusterPickingCommonCase):
    """Tests covering the /change_pack_lot endpoint

    Only simple cases are tested to check the flow of responses on success and
    error, the "change.package.lot" component is tested in its own tests.
    """

    @classmethod
    def setUpClassBaseData(cls, *args, **kwargs):
        super(ClusterPickingChangePackLotCase, cls).setUpClassBaseData(*args, **kwargs)
        cls.batch = cls._create_picking_batch(
            [[cls.BatchProduct(product=cls.product_a, quantity=10)]]
        )
        cls.bin1 = cls.env["stock.quant.package"].create({})

    def _test_change_pack_lot(
        self,
        operation,
        barcode,
        lot=None,
        success=True,
        message=None,
        new_lot=None,
        package_dest=None,
    ):
        batch = operation.picking_id.batch_id
        params = {
            "picking_batch_id": batch.id,
            "operation_id": operation.id,
            "barcode": barcode,
        }
        if lot:
            params["lot_id"] = lot.id
        response = self.service.dispatch("change_pack_lot", params=params,)
        if success:
            self.assert_response(
                response,
                message=message,
                next_state="scan_destination",
                data=self._operation_data(
                    operation, package_dest=package_dest, force_lot=new_lot
                ),
            )
        else:
            self.assert_response(
                response,
                message=message,
                next_state="change_pack_lot",
                data=self._operation_data(operation),
            )
        return response

    def assertLotOperation(self, picking, lot, qty_todo, qty_done):
        pack_lots = picking.mapped("pack_operation_ids.pack_lot_ids").filtered(
            lambda pl, lot=lot: pl.lot_id == lot
        )
        self.assertTrue(pack_lots, "No operation found for lot %s" % lot.name)
        pack_qty_done = sum(pack_lots.mapped("qty"))
        pack_qty_todo = sum(pack_lots.mapped("qty_todo"))
        self.assertEqual(qty_todo, pack_qty_todo)
        self.assertEqual(qty_done, pack_qty_done)

    @unittest.skip("Change package not implemented")
    def test_change_pack_lot_change_pack_ok(self):
        initial_package = self._create_package_in_location(
            self.shelf1, [self.PackageContent(self.product_a, 10, lot=None)]
        )
        self._simulate_batch_selected(self.batch, fill_stock=False)

        # ensure we have our new package in the same location
        new_package = self._create_package_in_location(
            self.shelf1, [self.PackageContent(self.product_a, 10, lot=None)]
        )

        operation = self.batch.picking_ids.pack_operation_ids
        self._test_change_pack_lot(
            operation,
            new_package.name,
            success=True,
            message=self.service.msg_store.package_replaced_by_package(
                initial_package, new_package
            ),
        )

        self.assertRecordValues(
            operation,
            [
                {
                    "package_id": new_package.id,
                    "result_package_id": new_package.id,
                    "product_qty": 10.0,
                }
            ],
        )
        self.assertRecordValues(
            operation.package_level_id, [{"package_id": new_package.id}]
        )

    def test_change_pack_lot_change_lot_ok(self):
        self.product_a.tracking = "lot"
        initial_lot = self._create_lot(self.product_a)
        self._update_qty_in_location(self.shelf1, self.product_a, 10, lot=initial_lot)
        self._simulate_batch_selected(self.batch, fill_stock=False)
        operation = self.batch.picking_ids.pack_operation_ids
        source_location = operation.location_id
        new_lot = self._create_lot(self.product_a)
        # ensure we have our new package in the same location
        self._update_qty_in_location(
            source_location, operation.product_id, 10, lot=new_lot
        )
        self._test_change_pack_lot(
            operation,
            new_lot.name,
            lot=initial_lot,
            success=True,
            message=self.service.msg_store.lot_replaced_by_lot(initial_lot, new_lot),
            new_lot=new_lot,
        )
        self.assertRecordValues(operation.pack_lot_ids, [{"lot_id": new_lot.id}])

    def test_change_pack_lot_with_same_lot_ok(self):
        self.product_a.tracking = "lot"
        initial_lot = self._create_lot(self.product_a)
        self._update_qty_in_location(self.shelf1, self.product_a, 10, lot=initial_lot)
        self._simulate_batch_selected(self.batch, fill_stock=False)
        operation = self.batch.picking_ids.pack_operation_ids
        new_lot = initial_lot

        batch = operation.picking_id.batch_id
        params = {
            "picking_batch_id": batch.id,
            "operation_id": operation.id,
            "barcode": new_lot.name,
            "lot_id": initial_lot.id,
        }
        response = self.service.dispatch("change_pack_lot", params=params,)
        message = self.msg_store.same_lot_selected(new_lot)
        self.assert_response(
            response,
            message=message,
            next_state="change_pack_lot",
            data=self._operation_data(operation),
        )

    def test_change_pack_lot_change_lot_existing_lot_01(self):
        """
        Data:
            Lot A / 5 to do / 0 done
            Lot B / 5 to do / 0 done
        Test Case:
            Replace lot A by lot B
        Expected Result:
            Lot B / 15 to do / 0 done
            Returned operation: Lot B to do
        """
        self.product_a.tracking = "lot"
        lot_a = self._create_lot(self.product_a)
        lot_b = self._create_lot(self.product_a)
        self._update_qty_in_location(self.shelf1, self.product_a, 5, lot=lot_a)
        self._update_qty_in_location(self.shelf1, self.product_a, 5, lot=lot_b)
        self._simulate_batch_selected(self.batch, fill_stock=False)
        # the batch should only contains 1 operation for 2 lotS
        self.assertEqual(1, len(self.batch.pack_operation_ids))
        self.assertEqual(2, len(self.batch.pack_operation_ids.pack_lot_ids))
        next_operation = self.service._next_operation_for_pick(self.batch)
        operation = self.data.operations(next_operation)[0]
        self.assertEqual(operation["lot"]["id"], lot_a.id)
        self.assertEqual(operation["quantity"], 5)
        response = self._test_change_pack_lot(
            next_operation,
            lot_b.name,
            lot=lot_a,
            success=True,
            message=self.service.msg_store.lot_replaced_by_lot(lot_a, lot_b),
            new_lot=lot_b,
        )
        # the batch should only contains 1 operation for 1 lotS
        self.assertEqual(1, len(self.batch.pack_operation_ids))
        self.assertEqual(1, len(self.batch.pack_operation_ids.pack_lot_ids))
        operation = response["data"]["scan_destination"]
        self.assertEqual(operation["lot"]["id"], lot_b.id)
        self.assertEqual(operation["quantity"], 10)

    def test_change_pack_lot_change_lot_existing_lot_02(self):
        """
        Data:
            Lot A / 5 to do / 0 done
            Lot B / 5 to do / 0 done
            Lot C nothing to do
        Test Case:
            Replace lot A by lot C
        Expected Result:
            Lot C / 10 to do / 0 done
            Lot B / 5 to do / 0 done
            Returned operation: Lot C to do
        """
        self.product_a.tracking = "lot"
        lot_a = self._create_lot(self.product_a)
        lot_b = self._create_lot(self.product_a)
        self._update_qty_in_location(self.shelf1, self.product_a, 5, lot=lot_a)
        self._update_qty_in_location(self.shelf1, self.product_a, 5, lot=lot_b)
        self._simulate_batch_selected(self.batch, fill_stock=False)
        # the batch should only contains 1 operation for 2 lotS
        self.assertEqual(1, len(self.batch.pack_operation_ids))
        self.assertEqual(2, len(self.batch.pack_operation_ids.pack_lot_ids))
        # create lot_c after the reservation to be sure it's not reserved by the picking
        lot_c = self._create_lot(self.product_a)
        self._update_qty_in_location(self.shelf1, self.product_a, 5, lot=lot_c)
        next_operation = self.service._next_operation_for_pick(self.batch)
        operation = self.data.operations(next_operation)[0]
        self.assertEqual(operation["lot"]["id"], lot_a.id)
        self.assertEqual(operation["quantity"], 5)
        response = self._test_change_pack_lot(
            next_operation,
            lot_c.name,
            lot=lot_a,
            success=True,
            message=self.service.msg_store.lot_replaced_by_lot(lot_a, lot_c),
            new_lot=lot_c,
        )
        # the batch should only contains 1 operation for 2 lotS
        self.assertEqual(1, len(self.batch.pack_operation_ids))
        self.assertEqual(2, len(self.batch.pack_operation_ids.pack_lot_ids))
        operation = response["data"]["scan_destination"]
        self.assertEqual(operation["lot"]["id"], lot_c.id)
        self.assertEqual(operation["quantity"], 5)

    def test_change_pack_lot_change_lot_existing_lot_03(self):
        """
        Data:
            Lot A / 5 to do / 3 done
            Lot B / 5 to do / 0 done
        Test Case:
            Replace lot A by lot B
        Expected Result:
            Lot A / 3 to do / 3 done
            Lot B / 7 to do / 0 done
            Returned operation: Lot B to do
        """
        self.product_a.tracking = "lot"
        lot_a = self._create_lot(self.product_a)
        lot_b = self._create_lot(self.product_a)
        self._update_qty_in_location(self.shelf1, self.product_a, 5, lot=lot_a)
        self._update_qty_in_location(self.shelf1, self.product_a, 5, lot=lot_b)
        self._simulate_batch_selected(self.batch, fill_stock=False)
        # the batch should only contains 1 operation for 2 lotS
        self.assertEqual(1, len(self.batch.pack_operation_ids))
        self.assertEqual(2, len(self.batch.pack_operation_ids.pack_lot_ids))
        next_operation = self.service._next_operation_for_pick(self.batch)
        operation = self.data.operations(next_operation)[0]
        self.assertEqual(operation["lot"]["id"], lot_a.id)
        self.assertEqual(operation["quantity"], 5)
        # process partially the first lot
        response = self.service.dispatch(
            "scan_destination_pack",
            params={
                "picking_batch_id": self.batch.id,
                "operation_id": next_operation.id,
                "barcode": self.bin1.name,
                "quantity": 3,
                "lot_id": lot_a.id,
            },
        )
        # we shoudl get a new start_operation data with an operation
        # on lot A for 2
        data = response["data"]["start_operation"]
        self.assertEqual(data["lot"]["id"], lot_a.id)
        self.assertEqual(data["quantity"], 2)
        next_operation = self.service._next_operation_for_pick(self.batch)
        self.assertEqual(next_operation.id, data["id"])
        # change lot
        response = self._test_change_pack_lot(
            next_operation,
            lot_b.name,
            lot=lot_a,
            success=True,
            message=self.service.msg_store.lot_replaced_by_lot(lot_a, lot_b),
            new_lot=lot_b,
            package_dest=self.bin1,
        )
        operation = response["data"]["scan_destination"]
        self.assertEqual(operation["lot"]["id"], lot_b.id)
        self.assertEqual(operation["quantity"], 7)
        self.assertLotOperation(self.batch.picking_ids, lot_a, 3, 3)
        self.assertLotOperation(self.batch.picking_ids, lot_b, 7, 0)

    def test_change_pack_lot_change_lot_existing_lot_04(self):
        """
        Data:
            Lot A / 5 to do / 3 done
            Lot B / 5 to do / 0 done
            Lot C nothing to do
        Test Case:
            Replace lot A by lot C
        Expected Result:
            Lot A / 3 to do / 3 done
            Lot B / 5 to do / 0 done
            Lot C / 2 to do / 0 done
            Returned operation: Lot C to do
        """
        self.product_a.tracking = "lot"
        lot_a = self._create_lot(self.product_a)
        lot_b = self._create_lot(self.product_a)
        self._update_qty_in_location(self.shelf1, self.product_a, 5, lot=lot_a)
        self._update_qty_in_location(self.shelf1, self.product_a, 5, lot=lot_b)
        self._simulate_batch_selected(self.batch, fill_stock=False)
        # the batch should only contains 1 operation for 2 lotS
        self.assertEqual(1, len(self.batch.pack_operation_ids))
        self.assertEqual(2, len(self.batch.pack_operation_ids.pack_lot_ids))
        next_operation = self.service._next_operation_for_pick(self.batch)
        operation = self.data.operations(next_operation)[0]
        self.assertEqual(operation["lot"]["id"], lot_a.id)
        self.assertEqual(operation["quantity"], 5)
        # create lot_c after the reservation to be sure it's not reserved by the picking
        lot_c = self._create_lot(self.product_a)
        self._update_qty_in_location(self.shelf1, self.product_a, 5, lot=lot_c)
        # process partially the first lot
        response = self.service.dispatch(
            "scan_destination_pack",
            params={
                "picking_batch_id": self.batch.id,
                "operation_id": next_operation.id,
                "barcode": self.bin1.name,
                "quantity": 3,
                "lot_id": lot_a.id,
            },
        )
        # we should get a new start_operation data with an operation
        # on lot A for 2
        data = response["data"]["start_operation"]
        self.assertEqual(data["lot"]["id"], lot_a.id)
        self.assertEqual(data["quantity"], 2)
        next_operation = self.service._next_operation_for_pick(self.batch)
        self.assertEqual(next_operation.id, data["id"])
        # change lot
        response = self._test_change_pack_lot(
            next_operation,
            lot_c.name,
            lot=lot_a,
            success=True,
            message=self.service.msg_store.lot_replaced_by_lot(lot_a, lot_c),
            new_lot=lot_c,
            package_dest=self.bin1,
        )
        operation = response["data"]["scan_destination"]
        self.assertEqual(operation["lot"]["id"], lot_c.id)
        self.assertEqual(operation["quantity"], 2)
        self.assertLotOperation(self.batch.picking_ids, lot_a, 3, 3)
        self.assertLotOperation(self.batch.picking_ids, lot_b, 5, 0)
        self.assertLotOperation(self.batch.picking_ids, lot_c, 2, 0)

    def test_change_pack_lot_change_lot_existing_lot_05(self):
        """
        Data:
            Lot A / 5 to do / 5 done
            Lot B / 5 to do / 0 done
        Test Case:
            Replace lot B by lot A
        Expected Result:
            Lot A / 10 to do / 5 done
            Returned operation: Lot A to do
        """
        self.product_a.tracking = "lot"
        lot_a = self._create_lot(self.product_a)
        lot_b = self._create_lot(self.product_a)
        self._update_qty_in_location(self.shelf1, self.product_a, 5, lot=lot_a)
        self._update_qty_in_location(self.shelf1, self.product_a, 5, lot=lot_b)
        self._simulate_batch_selected(self.batch, fill_stock=False)
        # the batch should only contains 1 operation for 2 lotS
        self.assertEqual(1, len(self.batch.pack_operation_ids))
        self.assertEqual(2, len(self.batch.pack_operation_ids.pack_lot_ids))
        next_operation = self.service._next_operation_for_pick(self.batch)
        operation = self.data.operations(next_operation)[0]
        self.assertEqual(operation["lot"]["id"], lot_a.id)
        self.assertEqual(operation["quantity"], 5)
        # process the first lot
        response = self.service.dispatch(
            "scan_destination_pack",
            params={
                "picking_batch_id": self.batch.id,
                "operation_id": next_operation.id,
                "barcode": self.bin1.name,
                "quantity": 5,
                "lot_id": lot_a.id,
            },
        )
        # we should get a new start_operation data with an operation
        # on lot b for 5
        data = response["data"]["start_operation"]
        self.assertEqual(data["lot"]["id"], lot_b.id)
        self.assertEqual(data["quantity"], 5)
        next_operation = self.service._next_operation_for_pick(self.batch)
        self.assertEqual(next_operation.id, data["id"])
        # change lot
        response = self._test_change_pack_lot(
            next_operation,
            lot_a.name,
            lot=lot_b,
            success=True,
            message=self.service.msg_store.lot_replaced_by_lot(lot_b, lot_a),
            new_lot=lot_a,
            package_dest=self.bin1,
        )
        operation = response["data"]["scan_destination"]
        self.assertEqual(operation["lot"]["id"], lot_a.id)
        self.assertEqual(operation["quantity"], 5)
        self.assertLotOperation(self.batch.picking_ids, lot_a, 10, 5)
        self.assertNotIn(
            lot_b, self.batch.pack_operation_ids.mapped("pack_lot_ids.lot_id")
        )

    def test_change_pack_lot_change_lot_existing_lot_06(self):
        """
        Data:
            Lot A / 5 to do / 5 done
            Lot B / 5 to do / 3 done
        Test Case:
            Replace lot B by lot A
        Expected Result:
            Lot A / 7 to do / 5 done
            Lot B / 3 to do / 3 done
            Returned operation: Lot A to do
        """
        self.product_a.tracking = "lot"
        lot_a = self._create_lot(self.product_a)
        lot_b = self._create_lot(self.product_a)
        self._update_qty_in_location(self.shelf1, self.product_a, 5, lot=lot_a)
        self._update_qty_in_location(self.shelf1, self.product_a, 5, lot=lot_b)
        self._simulate_batch_selected(self.batch, fill_stock=False)
        # the batch should only contains 1 operation for 2 lotS
        self.assertEqual(1, len(self.batch.pack_operation_ids))
        self.assertEqual(2, len(self.batch.pack_operation_ids.pack_lot_ids))
        next_operation = self.service._next_operation_for_pick(self.batch)
        operation = self.data.operations(next_operation)[0]
        self.assertEqual(operation["lot"]["id"], lot_a.id)
        self.assertEqual(operation["quantity"], 5)
        # process the first lot
        response = self.service.dispatch(
            "scan_destination_pack",
            params={
                "picking_batch_id": self.batch.id,
                "operation_id": next_operation.id,
                "barcode": self.bin1.name,
                "quantity": 5,
                "lot_id": lot_a.id,
            },
        )
        # we should get a new start_operation data with an operation
        # on lot b for 5
        data = response["data"]["start_operation"]
        self.assertEqual(data["lot"]["id"], lot_b.id)
        self.assertEqual(data["quantity"], 5)
        next_operation = self.service._next_operation_for_pick(self.batch)
        self.assertEqual(next_operation.id, data["id"])
        # partial process lob b
        response = self.service.dispatch(
            "scan_destination_pack",
            params={
                "picking_batch_id": self.batch.id,
                "operation_id": next_operation.id,
                "barcode": self.bin1.name,
                "quantity": 3,
                "lot_id": lot_b.id,
            },
        )
        # we should get a new start_operation data with an operation
        # on lot b for 2
        data = response["data"]["start_operation"]
        self.assertEqual(data["lot"]["id"], lot_b.id)
        self.assertEqual(data["quantity"], 2)
        next_operation = self.service._next_operation_for_pick(self.batch)
        # change lot
        response = self._test_change_pack_lot(
            next_operation,
            lot_a.name,
            lot=lot_b,
            success=True,
            message=self.service.msg_store.lot_replaced_by_lot(lot_b, lot_a),
            new_lot=lot_a,
            package_dest=self.bin1,
        )
        operation = response["data"]["scan_destination"]
        self.assertEqual(operation["lot"]["id"], lot_a.id)
        self.assertEqual(operation["quantity"], 2)
        self.assertLotOperation(self.batch.picking_ids, lot_a, 7, 5)
        self.assertLotOperation(self.batch.picking_ids, lot_b, 3, 3)

    def test_change_pack_lot_change_error(self):
        self.product_a.tracking = "lot"
        initial_lot = self._create_lot(self.product_a)
        self._update_qty_in_location(self.shelf1, self.product_a, 10, lot=initial_lot)
        self._simulate_batch_selected(self.batch, fill_stock=False)
        operation = self.batch.picking_ids.pack_operation_ids
        # ensure we have our new package in the same location
        self._test_change_pack_lot(
            operation,
            "NOT_FOUND",
            lot=initial_lot,
            success=False,
            message=self.service.msg_store.no_package_or_lot_for_barcode("NOT_FOUND"),
        )

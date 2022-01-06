# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.alc_shopfloor.tests.test_cluster_picking_unload import (
    ClusterPickingUnloadingCommonCase,
)


# pylint: disable=missing-return
class ClusterPickingUnloadPackingCommonCase(ClusterPickingUnloadingCommonCase):
    @classmethod
    def setUpClassBaseData(cls, *args, **kwargs):
        super(ClusterPickingUnloadPackingCommonCase, cls).setUpClassBaseData(
            *args, **kwargs
        )
        cls.bin1.write({"name": "bin1", "is_internal": True})
        cls.bin2.write({"name": "bin2", "is_internal": True})
        cls.menu.sudo().pack_pickings = True


class TestClusterPickingPrepareUnload(ClusterPickingUnloadPackingCommonCase):
    def test_scan_destination_pack_bin_not_internal(self):
        """Scan a destination package that is not an internal package"""
        self.bin2.is_internal = False
        operation = self.pack_operation_ids[0]
        response = self.service.dispatch(
            "scan_destination_pack",
            params={
                "picking_batch_id": self.batch.id,
                "operation_id": operation.id,
                # this bin is used for the other picking
                "barcode": self.bin2.name,
                "quantity": operation.product_qty,
            },
        )
        self.assert_response(
            response,
            next_state="scan_destination",
            data=self._operation_data(operation),
            message=self.service.msg_store.bin_should_be_internal(self.bin2),
        )

    def test_prepare_unload_all_same_dest(self):
        operations = self.pack_operation_ids
        self._set_dest_package_and_done(operations[:1], self.bin2)
        self._set_dest_package_and_done(operations[1:], self.bin1)
        operations.write({"location_dest_id": self.packing_location.id})
        response = self.service.dispatch(
            "prepare_unload", params={"picking_batch_id": self.batch.id}
        )
        location = self.packing_location
        # The first bin to process is bin1 we should therefore scan the bin 1
        # to pack and put in pack
        picking = operations[-1].picking_id
        data = self.data_detail.pack_picking_detail(picking)
        self.assert_response(
            response, next_state="pack_picking_scan_pack", data=data,
        )
        # we scan the pack
        response = self.service.dispatch(
            "scan_packing_to_pack",
            params={
                "picking_batch_id": self.batch.id,
                "picking_id": picking.id,
                "barcode": self.bin1.name,
            },
        )
        data = self.data_detail.pack_picking_detail(picking)
        self.assert_response(
            response, next_state="pack_picking_put_in_pack", data=data,
        )
        # we process to the put in pack
        response = self.service.dispatch(
            "put_in_pack",
            params={
                "picking_batch_id": self.batch.id,
                "picking_id": picking.id,
                "nbr_packages": 4,
            },
        )
        message = self.service.msg_store.stock_picking_packed_successfully(picking)
        result_package = picking.pack_operation_ids.mapped("result_package_id")
        self.assertEqual(len(result_package), 1)
        self.assertEqual(result_package[0].nbr_packages, 4)

        picking = operations[0].picking_id
        data = self.data_detail.pack_picking_detail(picking)
        # message = self.service.msg_store.stock_picking_packed_successfully(picking)
        self.assert_response(
            response, next_state="pack_picking_scan_pack", data=data, message=message
        )
        # we scan the pack
        response = self.service.dispatch(
            "scan_packing_to_pack",
            params={
                "picking_batch_id": self.batch.id,
                "picking_id": picking.id,
                "barcode": self.bin2.name,
            },
        )
        data = self.data_detail.pack_picking_detail(picking)
        self.assert_response(
            response, next_state="pack_picking_put_in_pack", data=data,
        )
        # we process to the put in pack
        response = self.service.dispatch(
            "put_in_pack",
            params={
                "picking_batch_id": self.batch.id,
                "picking_id": picking.id,
                "nbr_packages": 2,
            },
        )
        data = self._data_for_batch(self.batch, location)
        message = self.service.msg_store.stock_picking_packed_successfully(picking)
        self.assert_response(
            response, next_state="unload_all", data=data, message=message
        )

        result_package = picking.pack_operation_ids.mapped("result_package_id")
        self.assertEqual(len(result_package), 1)
        self.assertEqual(result_package[0].nbr_packages, 2)

    def test_prepare_unload_different_dest(self):
        """All move lines have different destination locations"""
        operations = self.pack_operation_ids
        self._set_dest_package_and_done(operations[:1], self.bin2)
        self._set_dest_package_and_done(operations[1:], self.bin1)
        operations[:1].write({"location_dest_id": self.packing_a_location.id})
        operations[1:].write({"location_dest_id": self.packing_b_location.id})
        response = self.service.dispatch(
            "prepare_unload", params={"picking_batch_id": self.batch.id}
        )
        # The first bin to process is bin1 we should therefore a pack_picking
        # step with the picking info of the last operation
        picking = operations[-1].picking_id
        data = self.data_detail.pack_picking_detail(picking)
        self.assert_response(
            response, next_state="pack_picking_scan_pack", data=data,
        )
        # we scan the pack
        response = self.service.dispatch(
            "scan_packing_to_pack",
            params={
                "picking_batch_id": self.batch.id,
                "picking_id": picking.id,
                "barcode": self.bin1.name,
            },
        )
        data = self.data_detail.pack_picking_detail(picking)
        self.assert_response(
            response, next_state="pack_picking_put_in_pack", data=data,
        )
        # we process to the put in pack
        response = self.service.dispatch(
            "put_in_pack",
            params={
                "picking_batch_id": self.batch.id,
                "picking_id": picking.id,
                "nbr_packages": 4,
            },
        )

        message = self.service.msg_store.stock_picking_packed_successfully(picking)

        # next picking..
        picking = operations[0].picking_id
        data = self.data_detail.pack_picking_detail(picking)
        self.assert_response(
            response, next_state="pack_picking_scan_pack", data=data, message=message
        )
        # we scan the pack
        response = self.service.dispatch(
            "scan_packing_to_pack",
            params={
                "picking_batch_id": self.batch.id,
                "picking_id": picking.id,
                "barcode": self.bin2.name,
            },
        )
        data = self.data_detail.pack_picking_detail(picking)
        self.assert_response(
            response, next_state="pack_picking_put_in_pack", data=data,
        )
        # we process to the put in pack
        response = self.service.dispatch(
            "put_in_pack",
            params={
                "picking_batch_id": self.batch.id,
                "picking_id": picking.id,
                "nbr_packages": 2,
            },
        )
        # Since the last operation has been put in pack first, the first pack
        # to unload is the one from the last operation
        new_bin = operations[-1].result_package_id
        location = operations[-1].location_dest_id
        data = self._data_for_batch(self.batch, location, pack=new_bin)
        message = self.service.msg_store.stock_picking_packed_successfully(picking)
        self.assert_response(
            response, next_state="unload_single", data=data, message=message
        )

    def test_prepare_full_bin_unload(self):
        # process one operation and call unload
        # the unload should return a pack_picking state
        # and once processed continue with next operations
        operations = self.pack_operation_ids
        self._set_dest_package_and_done(operations[0], self.bin1)
        operations.write({"location_dest_id": self.packing_location.id})
        response = self.service.dispatch(
            "prepare_unload", params={"picking_batch_id": self.batch.id}
        )
        # step with the picking info of the last operation
        picking = operations[0].picking_id
        data = self.data_detail.pack_picking_detail(picking)
        self.assert_response(
            response, next_state="pack_picking_scan_pack", data=data,
        )
        # we scan the pack and  process to the put in pack
        response = self.service.dispatch(
            "scan_packing_to_pack",
            params={
                "picking_batch_id": self.batch.id,
                "picking_id": picking.id,
                "barcode": self.bin1.name,
            },
        )
        data = self.data_detail.pack_picking_detail(picking)
        self.assert_response(
            response, next_state="pack_picking_put_in_pack", data=data,
        )
        response = self.service.dispatch(
            "put_in_pack",
            params={
                "picking_batch_id": self.batch.id,
                "picking_id": picking.id,
                "nbr_packages": 4,
            },
        )
        result_package = picking.pack_operation_ids.mapped("result_package_id")
        self.assertEqual(len(result_package), 1)
        self.assertEqual(result_package[0].nbr_packages, 4)

        # now we must unload
        location = operations[0].location_dest_id
        data = self._data_for_batch(self.batch, location)
        self.assert_response(
            response,
            next_state="unload_all",
            data=data,
            message=self.service.msg_store.stock_picking_packed_successfully(picking),
        )
        response = self.service.dispatch(
            "set_destination_all",
            params={
                "picking_batch_id": self.batch.id,
                "barcode": self.packing_location.barcode,
            },
        )

        # once the unload is done, we must process the others operations
        operation = self.service._next_operation_for_pick(self.batch)
        while operation:
            picking = operation.picking_id
            self.assertEqual(response["next_state"], "start_operation")
            response = self.service.dispatch(
                "scan_destination_pack",
                params={
                    "picking_batch_id": self.batch.id,
                    "operation_id": operation.id,
                    "barcode": self.bin1.name,
                    "quantity": operation.product_qty,
                },
            )
            operation = self.service._next_operation_for_pick(self.batch)

        # everything is processed, we should put in pack...
        data = self.data_detail.pack_picking_detail(picking)
        self.assert_response(
            response, next_state="pack_picking_scan_pack", data=data,
        )
        # we scan the pack and  process to the put in pack
        response = self.service.dispatch(
            "scan_packing_to_pack",
            params={
                "picking_batch_id": self.batch.id,
                "picking_id": picking.id,
                "barcode": self.bin1.name,
            },
        )
        data = self.data_detail.pack_picking_detail(picking)
        self.assert_response(
            response, next_state="pack_picking_put_in_pack", data=data,
        )
        response = self.service.dispatch(
            "put_in_pack",
            params={
                "picking_batch_id": self.batch.id,
                "picking_id": picking.id,
                "nbr_packages": 2,
            },
        )
        data = self._data_for_batch(self.batch, location)
        self.assert_response(
            response,
            next_state="unload_all",
            data=data,
            message=self.service.msg_store.stock_picking_packed_successfully(picking),
        )

        result_package = picking.pack_operation_ids.mapped("result_package_id")
        self.assertEqual(len(result_package), 1)
        self.assertEqual(result_package[0].nbr_packages, 2)

    def test_response_for_scan_destination(self):
        """Check that non internal package are not proposed as package_dest"""
        line1 = self.two_lines_picking.pack_operation_ids[0]
        # we already scan and put the first line in bin1
        self._set_dest_package_and_done(line1, self.bin1)
        self.bin1.is_internal = False
        self.assertFalse(self.service._last_picked_line(line1.picking_id))
        response = self.service._response_for_scan_destination(line1)
        self.assertFalse(response["data"]["scan_destination"]["package_dest"])

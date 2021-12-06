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


class ClusterPickingPrepareUnloadCase(ClusterPickingUnloadPackingCommonCase):
    def test_prepare_unload_all_same_dest(self):
        operations = self.pack_operation_ids
        self._set_dest_package_and_done(operations[:1], self.bin2)
        self._set_dest_package_and_done(operations[1:], self.bin1)
        operations.write({"location_dest_id": self.packing_location.id})
        response = self.service.dispatch(
            "prepare_unload", params={"picking_batch_id": self.batch.id}
        )
        location = self.packing_location
        # The first bin to process is bin1 we should therefore a pack_picking
        # step with the picking info of the last operation
        picking = operations[-1].picking_id
        data = self.data_detail.picking_detail(picking)
        self.assert_response(
            response, next_state="pack_picking", data=data,
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
        result_package = picking.pack_operation_ids.mapped("result_package_id")
        self.assertEqual(len(result_package), 1)
        self.assertEqual(result_package[0].nbr_packages, 4)

        picking = operations[0].picking_id
        data = self.data_detail.picking_detail(picking)
        self.assert_response(
            response, next_state="pack_picking", data=data,
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
        self.assert_response(
            response, next_state="unload_all", data=data,
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
        first_line = operations[0]
        location = first_line.location_dest_id
        # The first bin to process is bin1 we should therefore a pack_picking
        # step with the picking info of the last operation
        picking = operations[-1].picking_id
        data = self.data_detail.picking_detail(picking)
        self.assert_response(
            response, next_state="pack_picking", data=data,
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

        picking = operations[0].picking_id
        data = self.data_detail.picking_detail(picking)
        self.assert_response(
            response, next_state="pack_picking", data=data,
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
        self.assert_response(
            response, next_state="unload_single", data=data,
        )

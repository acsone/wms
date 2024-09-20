# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import Command

from odoo.addons.shopfloor_packing.tests.common import ClusterPickingUnloadingCommonCase


class TestOutLocationsClusterPicking(ClusterPickingUnloadingCommonCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.menu.sudo().unload_on_specific_location = True
        cls.out_location = cls.env.ref("stock.stock_location_output")
        cls.out_location1 = (
            cls.env["stock.location"]
            .sudo()
            .create(
                {
                    "name": "TestOutLocation1",
                    "location_id": cls.out_location.id,
                    "keep_track_of_release_channel": True,
                }
            )
        )

        cls.out_location2 = (
            cls.env["stock.location"]
            .sudo()
            .create(
                {
                    "name": "TestOutLocation2",
                    "location_id": cls.out_location.id,
                    "keep_track_of_release_channel": True,
                }
            )
        )

        cls.out_location1_level1 = (
            cls.env["stock.location"]
            .sudo()
            .create(
                {
                    "name": "TestOutLevel1Location1",
                    "location_id": cls.out_location1.id,
                    "keep_track_of_release_channel": True,
                }
            )
        )
        cls.out_location2_level1 = (
            cls.env["stock.location"]
            .sudo()
            .create(
                {
                    "name": "TestOutLevel1Location2",
                    "location_id": cls.out_location2.id,
                    "keep_track_of_release_channel": True,
                }
            )
        )
        cls.env["stock.location"]._parent_store_compute()
        cls.release_channel = (
            cls.env["stock.release.channel"].sudo().create({"name": "channel 1"})
        )
        cls.release_channel2 = (
            cls.env["stock.release.channel"].sudo().create({"name": "channel 2"})
        )

        cls._set_dest_package_and_done(cls.move_lines[:1], cls.bin2)
        cls._set_dest_package_and_done(cls.move_lines[1:], cls.bin1)
        cls.move_lines.write({"location_dest_id": cls.out_location.id})
        cls.batch.picking_ids.write({"location_dest_id": cls.out_location.id})

    def _prepare_out_packages(self, batch, move_lines):
        self.service.dispatch("prepare_unload", params={"picking_batch_id": batch.id})
        result_packages = move_lines.mapped("result_package_id")
        return result_packages

    def test_00_unload_specific_location_and_deliver(self):
        self.batch.picking_ids.write({"release_channel_id": self.release_channel.id})
        packs_to_unload = self._prepare_out_packages(self.batch, self.move_lines)
        pack1 = packs_to_unload[0]
        pack2 = packs_to_unload[1]
        response = self.service.dispatch(
            "unload_scan_pack",
            params={
                "picking_batch_id": self.batch.id,
                "package_id": pack1.id,
                "barcode": pack1.name,
            },
        )
        data = self._data_for_batch(self.batch, location=self.out_location, pack=pack1)
        self.assert_response(
            response,
            next_state="unload_set_destination",
            data=data,
        )

        response = self.service.dispatch(
            "unload_scan_destination",
            params={
                "picking_batch_id": self.batch.id,
                "package_id": pack1.id,
                "barcode": self.out_location1_level1.name,
            },
        )
        self.assertEqual(self.out_location1.release_channel_id, self.release_channel)
        data = self._data_for_batch(self.batch, location=self.out_location, pack=pack2)
        self.assert_response(
            response,
            next_state="unload_single",
            data=data,
        )

        response = self.service.dispatch(
            "unload_scan_pack",
            params={
                "picking_batch_id": self.batch.id,
                "package_id": pack2.id,
                "barcode": pack2.name,
            },
        )
        data = self._data_for_batch(self.batch, location=self.out_location, pack=pack2)
        self.assert_response(
            response,
            next_state="unload_set_destination",
            data=data,
        )

        response = self.service.dispatch(
            "unload_scan_destination",
            params={
                "picking_batch_id": self.batch.id,
                "package_id": pack2.id,
                "barcode": self.out_location1_level1.name,
            },
        )
        self.assert_response(
            response,
            next_state="start",
            message={"body": "Batch Transfer complete", "message_type": "success"},
        )

        self.release_channel._action_deliver()
        self.assertFalse(self.out_location1.release_channel_id)

    def test_01_do_not_mix_release_channels(self):
        pickings = self.batch.picking_ids
        pick1 = pickings[0]
        pick2 = pickings[1]
        pick1.release_channel_id = self.release_channel
        pick2.release_channel_id = self.release_channel2

        packs_to_unload = self._prepare_out_packages(self.batch, self.move_lines)
        pack1 = packs_to_unload[0]
        pack2 = packs_to_unload[1]
        response = self.service.dispatch(
            "unload_scan_pack",
            params={
                "picking_batch_id": self.batch.id,
                "package_id": pack1.id,
                "barcode": pack1.name,
            },
        )
        data = self._data_for_batch(self.batch, location=self.out_location, pack=pack1)
        self.assert_response(
            response,
            next_state="unload_set_destination",
            data=data,
        )
        response = self.service.dispatch(
            "unload_scan_destination",
            params={
                "picking_batch_id": self.batch.id,
                "package_id": pack1.id,
                "barcode": self.out_location1_level1.name,
            },
        )
        data = self._data_for_batch(self.batch, location=self.out_location, pack=pack2)
        self.assert_response(
            response,
            next_state="unload_single",
            data=data,
        )
        response = self.service.dispatch(
            "unload_scan_pack",
            params={
                "picking_batch_id": self.batch.id,
                "package_id": pack2.id,
                "barcode": pack2.name,
            },
        )
        data = self._data_for_batch(self.batch, location=self.out_location, pack=pack2)
        self.assert_response(
            response,
            next_state="unload_set_destination",
            data=data,
        )
        response = self.service.dispatch(
            "unload_scan_destination",
            params={
                "picking_batch_id": self.batch.id,
                "package_id": pack2.id,
                "barcode": self.out_location1_level1.name,
            },
        )
        self.assert_response(
            response,
            next_state="unload_set_destination",
            data=data,
            message={
                "body": "This trolley is already blocked by another release channel, select a new one.",
                "message_type": "error",
            },
        )
        response = self.service.dispatch(
            "unload_scan_destination",
            params={
                "picking_batch_id": self.batch.id,
                "package_id": pack2.id,
                "barcode": self.out_location2_level1.name,
            },
        )
        self.assert_response(
            response,
            next_state="start",
            message={"body": "Batch Transfer complete", "message_type": "success"},
        )

    def test_02_unload_wrong_package(self):
        self.bin3 = self.env["stock.quant.package"].create({})
        pick = self.env["stock.picking"].create(
            {
                "partner_id": self.customer.id,
                "picking_type_id": self.picking_type.id,
                "location_id": self.picking_type.default_location_src_id.id,
                "location_dest_id": self.picking_type.default_location_dest_id.id,
                "move_line_ids": [
                    Command.create(
                        {
                            "product_id": self.product_b.id,
                            "picking_type_id": self.picking_type.id,
                            "reserved_uom_qty": 10,
                            "location_id": self.picking_type.default_location_src_id.id,
                            "location_dest_id": self.picking_type.default_location_dest_id.id,
                        },
                    ),
                ],
            }
        )
        self.batch2 = self.env["stock.picking.batch"].create(
            {"picking_ids": [Command.set(pick.ids)]}
        )
        self.batch2.picking_ids.action_confirm()
        self.batch2.picking_ids.action_assign()

        self.move_lines2 = self.batch2.picking_ids.mapped("move_line_ids")
        self._set_dest_package_and_done(self.move_lines2[:1], self.bin3)
        self.move_lines2.write({"location_dest_id": self.out_location.id})
        self.batch2.picking_ids.write({"location_dest_id": self.out_location.id})
        packs_to_unload = self._prepare_out_packages(self.batch2, self.move_lines2)
        pack1 = packs_to_unload[0]
        packs_batch1 = self._prepare_out_packages(self.batch, self.move_lines)
        response = self.service.dispatch(
            "unload_scan_pack",
            params={
                "picking_batch_id": self.batch.id,
                "package_id": packs_batch1[0].id,
                "barcode": pack1.name,
            },
        )
        data = self._data_for_batch(self.batch, location=self.out_location, pack=pack1)

        self.assert_response(
            response,
            next_state="unload_single",
            data=data,
            message={
                "body": "Package not in the picking batch. Please scan a correct package.",
                "message_type": "error",
            },
        )

    def test_03_unload_not_existing_package(self):
        packs_batch1 = self._prepare_out_packages(self.batch, self.move_lines)
        response = self.service.dispatch(
            "unload_scan_pack",
            params={
                "picking_batch_id": self.batch.id,
                "package_id": packs_batch1[0].id,
                "barcode": "PACKDOESNOTEXIST",
            },
        )
        data = self._data_for_batch(
            self.batch, location=self.out_location, pack=packs_batch1[0]
        )

        self.assert_response(
            response,
            next_state="unload_single",
            data=data,
            message={
                "body": "Package does not exist. Please scan a correct package.",
                "message_type": "error",
            },
        )

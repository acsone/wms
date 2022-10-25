# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.addons.alc_shopfloor_packing.tests.test_cluster_picking_pack_picking import (
    ClusterPickingUnloadingCommonCase,
)


class TestOutLocationsClusterPicking(ClusterPickingUnloadingCommonCase):
    @classmethod
    def setUpClass(cls):
        super(TestOutLocationsClusterPicking, cls).setUpClass()
        cls.menu.sudo().unload_on_specific_location = True
        cls.out_location = cls.env.ref("stock.stock_location_output")
        cls.out_location1 = (
            cls.env["stock.location"]
            .sudo()
            .create(
                {
                    "name": "TestOutLocation1",
                    "location_id": cls.out_location.id,
                    "keep_track_of_delivery_round": True,
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
                    "keep_track_of_delivery_round": True,
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
                    "keep_track_of_delivery_round": True,
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
                    "keep_track_of_delivery_round": True,
                }
            )
        )
        cls.env["stock.location"]._parent_store_compute()
        cls.delivery_template = (
            cls.env["round.template"]
            .sudo()
            .create({"name": "Unittest delivery template"})
        )
        cls.delivery_round = (
            cls.env["round.instance"]
            .sudo()
            .create({"template_id": cls.delivery_template.id, "date": "2017-01-01"})
        )
        delivery_template2 = (
            cls.env["round.template"]
            .sudo()
            .create({"name": "Unittest delivery template2"})
        )
        cls.delivery_round2 = (
            cls.env["round.instance"]
            .sudo()
            .create({"template_id": delivery_template2.id, "date": "2017-01-01"})
        )

        cls.operations = cls.pack_operation_ids
        cls._set_dest_package_and_done(cls.operations[:1], cls.bin2)
        cls._set_dest_package_and_done(cls.operations[1:], cls.bin1)
        cls.operations.write({"location_dest_id": cls.out_location.id})
        cls.batch.picking_ids.write({"location_dest_id": cls.out_location.id})

    def _prepare_out_packages(self):
        self.service.dispatch(
            "prepare_unload", params={"picking_batch_id": self.batch.id}
        )
        result_packages = self.operations.mapped("result_package_id")
        return result_packages

    def test_00_unload_specific_location_and_deliver(self):
        self.delivery_round._assign_pickings(self.batch.picking_ids)
        packs_to_unload = self._prepare_out_packages()
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
            response, next_state="unload_set_destination", data=data,
        )

        response = self.service.dispatch(
            "unload_scan_destination",
            params={
                "picking_batch_id": self.batch.id,
                "package_id": pack1.id,
                "barcode": self.out_location1_level1.name,
            },
        )
        self.assertEqual(self.out_location1.delivery_round_id, self.delivery_round)
        data = self._data_for_batch(self.batch, location=self.out_location, pack=pack2)
        self.assert_response(
            response, next_state="unload_single", data=data,
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
            response, next_state="unload_set_destination", data=data,
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

        self.delivery_round.button_deliver()
        self.assertFalse(self.out_location1.delivery_round_id)

    def test_01_do_not_mix_delivery_rounds(self):
        pickings = self.batch.picking_ids
        pick1 = pickings[0]
        pick2 = pickings[1]
        self.delivery_round._assign_pickings(pick1)
        self.delivery_round2._assign_pickings(pick2)

        packs_to_unload = self._prepare_out_packages()
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
            response, next_state="unload_set_destination", data=data,
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
            response, next_state="unload_single", data=data,
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
            response, next_state="unload_set_destination", data=data,
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
                "body": "This trolley is already blocked by another delivery round, select a new one.",
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

    def test_02_cannot_unload_on_specific_locations(self):
        """ Carrier is specified to not unload on specific locations :
         redirection to unload_all as it previously was
        """
        carrier = (
            self.env["delivery.carrier"]
            .sudo()
            .create(
                {
                    "name": "Unittest delivery carrier",
                    "delivery_template_id": self.delivery_template.id,
                    "unload_on_specific_location": False,
                }
            )
        )
        wh = self.env.ref("stock.warehouse0")
        wh.sudo().write(
            {
                "name": "Test Warehouse",
                "reception_steps": "one_step",
                "delivery_steps": "pick_ship",
                "code": "TST",
            }
        )
        wh.sudo().pick_type_id.subcode = "PICK"
        partner = self.env["res.partner"].sudo().create({"name": "partner1"})
        so_values = {
            "partner_id": partner.id,
            "warehouse_id": wh.id,
            "carrier_id": carrier.id,
            "order_line": [
                (
                    0,
                    0,
                    {
                        "name": self.product_a.name,
                        "product_id": self.product_a.id,
                        "product_uom_qty": 1,
                        "product_uom": self.product_a.uom_id.id,
                        "price_unit": 1,
                    },
                )
            ],
        }

        new_so = self.env["sale.order"].sudo().create(so_values)
        new_so.action_confirm()
        pick = new_so.picking_ids.filtered(lambda p: p.picking_type_subcode == "PICK")
        batch = self.env["stock.picking.wave"].create(
            {"picking_ids": [(6, None, pick.ids)]}
        )
        batch.picking_ids.action_confirm()
        batch.picking_ids.action_assign()
        self.delivery_round._assign_pickings(self.batch.picking_ids)
        response = self.service.dispatch(
            "prepare_unload", params={"picking_batch_id": self.batch.id}
        )
        data = self._data_for_batch(self.batch, location=self.out_location)
        self.assert_response(
            response, next_state="unload_all", data=data,
        )

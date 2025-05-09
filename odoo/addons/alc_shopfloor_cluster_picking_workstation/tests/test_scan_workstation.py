# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.addons.shopfloor.tests.test_cluster_picking_unload import (
    ClusterPickingUnloadingCommonCase,
)


class TestScanWorkstation(ClusterPickingUnloadingCommonCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.workstation = (
            cls.env["shopfloor.workstation"]
            .sudo()
            .create({"name": "test_workstation", "barcode": "test_workstation"})
        )

        cls.bin1.write({"name": "bin1", "is_internal": True})
        cls.bin2.write({"name": "bin2", "is_internal": True})
        cls._set_dest_package_and_done(cls.move_lines[:1], cls.bin2)
        cls._set_dest_package_and_done(cls.move_lines[1:], cls.bin1)
        cls.move_lines.write({"location_dest_id": cls.packing_location.id})
        cls.menu.sudo().scan_workstation = True

    def test_scan_workstation_ok(self):
        response = self.service.dispatch(
            "prepare_unload", params={"picking_batch_id": self.batch.id}
        )
        expected = {"data": {}, "next_state": "scan_workstation"}
        self.assertEqual(response, expected)
        response = self.service.dispatch(
            "scan_workstation",
            params={
                "barcode": self.workstation.name,
                "picking_batch_id": self.batch.id,
            },
        )
        operations = self.move_lines
        picking = operations[-1].picking_id
        data = self.data.pack_picking(picking)
        self.assert_response(
            response,
            next_state="pack_picking_scan_pack",
            data=data,
            message=self.service.msg_store.workstation_set(self.workstation),
        )

    def test_scan_workstation_not_found(self):
        response = self.service.dispatch(
            "prepare_unload", params={"picking_batch_id": self.batch.id}
        )
        expected = {"data": {}, "next_state": "scan_workstation"}
        self.assertEqual(response, expected)
        response = self.service.dispatch(
            "scan_workstation",
            params={
                "barcode": "unknown_workstation",
                "picking_batch_id": self.batch.id,
            },
        )
        expected = {
            "data": {"scan_workstation": {}},
            "message": self.service.msg_store.workstation_not_found(),
            "next_state": "scan_workstation",
        }
        self.assertEqual(response, expected)

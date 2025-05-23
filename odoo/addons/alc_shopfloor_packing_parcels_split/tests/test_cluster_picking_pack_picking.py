# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.tests.common import RecordCapturer

from odoo.addons.shopfloor.tests.test_cluster_picking_unload import (
    ClusterPickingUnloadingCommonCase,
)


# pylint: disable=missing-return
class ClusterPickingPutInPackPrintCase(ClusterPickingUnloadingCommonCase):
    @classmethod
    def setUpClassBaseData(cls, *args, **kwargs):
        super().setUpClassBaseData(*args, **kwargs)
        cls.bin1.write({"name": "bin1", "is_internal": True})
        cls.bin2.write({"name": "bin2", "is_internal": True})
        cls.menu.sudo().write({"pack_pickings": True})
        cls.package_type = (
            cls.env["stock.package.type"]
            .sudo()
            .create(
                {
                    "name": "package type",
                    "number_of_parcels": 2,
                    "auto_distribute_products_in_parcels": True,
                }
            )
        )

    def test_put_in_pack_with_split(self):
        move_lines = self.move_lines
        self._set_dest_package_and_done(move_lines[:1], self.bin2)
        self._set_dest_package_and_done(move_lines[1:], self.bin1)
        move_lines.write({"location_dest_id": self.packing_location.id})
        response = self.service.dispatch(
            "prepare_unload", params={"picking_batch_id": self.batch.id}
        )

        # The first bin to process is bin1 scan the pack and try to put in pack
        picking = move_lines[-1].picking_id
        data = self.data.pack_picking(picking)
        self.assert_response(
            response,
            next_state="pack_picking_scan_pack",
            data=data,
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
        data = self.data.pack_picking(picking)
        self.assert_response(
            response,
            next_state="pack_picking_put_in_pack",
            data=data,
        )
        StockQuantPackage = self.env["stock.quant.package"].sudo()
        with RecordCapturer(StockQuantPackage, []) as rec:
            response = self.service.dispatch(
                "put_in_pack",
                params={
                    "picking_batch_id": self.batch.id,
                    "picking_id": picking.id,
                    "selected_line_ids": move_lines.ids,
                    "package_type_id": self.package_type.id,
                },
            )
            self.assertEqual(len(rec.records), 2)

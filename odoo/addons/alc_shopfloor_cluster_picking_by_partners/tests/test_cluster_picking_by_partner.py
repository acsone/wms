# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.shopfloor.tests.test_cluster_picking_base import (
    ClusterPickingCommonCase,
)


class TestClusterPickingByPartner(ClusterPickingCommonCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.env["stock.picking.batch"].search([]).unlink()
        cls.device1 = cls._create_device("device1", 0, 300, 300, 8, 50)
        cls.menu.sudo().write(
            {
                "batch_create": True,
                "group_pickings_by_partner": True,
                "multiple_move_single_pack": True,
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
        cls.picking = cls._create_picking(
            picking_type=cls.picking_type, lines=[(cls.product_a, 3)]
        )
        cls._fill_stock_for_moves(cls.picking.move_ids)
        cls.picking.action_confirm()
        cls.picking1 = cls._create_picking(
            picking_type=cls.picking_type, lines=[(cls.product_b, 1)]
        )
        cls._fill_stock_for_moves(cls.picking1.move_ids)
        cls.picking1.action_confirm()
        (cls.product_a | cls.product_b).write({"weight": 1, "volume": 2})
        cls.picking.action_assign()
        cls.picking1.action_assign()

    @classmethod
    def _create_device(
        cls, name, min_volume, max_volume, max_weight, nbr_bins, sequence
    ):
        return cls.env["stock.device.type"].create(
            {
                "name": name,
                "min_volume": min_volume,
                "max_volume": max_volume,
                "max_weight": max_weight,
                "nbr_bins": nbr_bins,
                "sequence": sequence,
            }
        )

    def setUp(self):
        super().setUp()
        context = dict(self.service.env.context)
        context.update({"test__ignore_label_print": True})
        self.service.env.context = context
        # self.picking1.move_ids.volume = 2
        # self.picking.move_ids.volume = 2

    def test_00(self):
        """Make sure batch is correctly created."""
        self.assertEqual(self.picking.volume, 6)
        self.assertEqual(self.picking1.volume, 2)
        response = self.service.dispatch("find_batch")
        data = self.data.picking_batch(self.picking.batch_id, with_pickings=True)
        self.assert_response(
            response,
            next_state="confirm_start",
            data=data,
        )
        batch = self.env["stock.picking.batch"].browse(data["id"])
        self.assertEqual(batch.user_id, self.shopfloor_user)
        self.assertEqual(batch.state, "in_progress")
        self.assertEqual(batch.batch_nbr_bins, 1)

    def test_01(self):
        """
        Group by partner is set to False.

        line from a different partner is  accepted in the same bin
        """
        self.menu.sudo().group_pickings_by_partner = False
        self.picking.partner_id = self.customer1
        self.picking1.partner_id = self.customer2
        line1 = self.picking.move_line_ids[0]
        line2 = self.picking1.move_line_ids[0]
        response = self.service.dispatch("find_batch")
        data = self.data.picking_batch(self.picking.batch_id, with_pickings=True)
        self.assert_response(
            response,
            next_state="confirm_start",
            data=data,
        )
        batch = self.picking.batch_id
        response = self.service.dispatch(
            "scan_line",
            params={
                "picking_batch_id": batch.id,
                "move_line_id": line1.id,
                "barcode": line1.product_id.barcode,
            },
        )
        self.assert_response(
            response,
            next_state="scan_destination",
            data=self._line_data(line1, qty_done=3.0),
        )
        qty_done1 = line1.reserved_uom_qty
        response = self.service.dispatch(
            "scan_destination_pack",
            params={
                "picking_batch_id": batch.id,
                "move_line_id": line1.id,
                "barcode": self.bin1.name,
                "quantity": qty_done1,
            },
        )
        self.assertRecordValues(
            line1, [{"qty_done": qty_done1, "result_package_id": self.bin1.id}]
        )
        self.assert_response(
            response,
            next_state="start_line",
            data=self._line_data(line2),
            message={
                "message_type": "success",
                "body": f"{line1.qty_done} {line1.product_id.display_name} put in {self.bin1.name}",
            },
        )
        qty_done2 = line2.reserved_uom_qty
        response = self.service.dispatch(
            "scan_destination_pack",
            params={
                "picking_batch_id": batch.id,
                "move_line_id": line2.id,
                "barcode": self.bin1.name,
                "quantity": qty_done2,
            },
        )
        self.assertRecordValues(
            line2, [{"qty_done": qty_done2, "result_package_id": self.bin1.id}]
        )
        operations = batch.picking_ids.mapped("move_line_ids")
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

    def test_02(self):
        """
        Group by partner is set to True.

        line from a different partner is not accepted in the same bin
        """
        self.picking.partner_id = self.customer1.id
        self.picking1.partner_id = self.customer2.id
        line1 = self.picking.move_line_ids[0]
        line2 = self.picking1.move_line_ids[0]
        response = self.service.dispatch("find_batch")
        data = self.data.picking_batch(self.picking.batch_id, with_pickings=True)
        self.assert_response(
            response,
            next_state="confirm_start",
            data=data,
        )
        batch = self.picking.batch_id
        response = self.service.dispatch(
            "scan_line",
            params={
                "picking_batch_id": batch.id,
                "move_line_id": line1.id,
                "barcode": line1.product_id.barcode,
            },
        )
        self.assert_response(
            response,
            next_state="scan_destination",
            data=self._line_data(line1, qty_done=3.0),
        )
        qty_done1 = line1.reserved_uom_qty
        response = self.service.dispatch(
            "scan_destination_pack",
            params={
                "picking_batch_id": batch.id,
                "move_line_id": line1.id,
                "barcode": self.bin1.name,
                "quantity": qty_done1,
            },
        )
        self.assertRecordValues(
            line1, [{"qty_done": qty_done1, "result_package_id": self.bin1.id}]
        )
        self.assert_response(
            response,
            next_state="start_line",
            data=self._line_data(line2),
            message={
                "message_type": "success",
                "body": f"{line1.qty_done} {line1.product_id.display_name} put in {self.bin1.name}",
            },
        )
        qty_done2 = line2.reserved_uom_qty
        response = self.service.dispatch(
            "scan_destination_pack",
            params={
                "picking_batch_id": batch.id,
                "move_line_id": line2.id,
                "barcode": self.bin1.name,
                "quantity": qty_done2,
            },
        )

        self.assert_response(
            response,
            next_state="scan_destination",
            data=self._line_data(line2, qty_done=1.0),
            message={
                "message_type": "error",
                "body": f"The destination bin {self.bin1.name} is not empty, please take another.",
            },
        )

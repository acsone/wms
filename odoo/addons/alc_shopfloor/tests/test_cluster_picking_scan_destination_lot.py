# -*- coding: utf-8 -*-
# Copyright 2020 Camptocamp SA (http://www.camptocamp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from .test_cluster_picking_base import ClusterPickingCommonCase


# pylint: disable=missing-return
class ClusterPickingScanDestinationLotPackCase(ClusterPickingCommonCase):
    """Tests covering the /scan_destination_pack endpoint

    After a batch has been selected and the user confirmed they are
    working on it, user picked the good, now they scan the location
    destination.
    """

    @classmethod
    def setUpClassBaseData(cls, *args, **kwargs):
        super(ClusterPickingScanDestinationLotPackCase, cls).setUpClassBaseData(
            *args, **kwargs
        )
        cls.batch = cls._create_picking_batch(
            [
                [
                    cls.BatchProduct(product=cls.product_a, quantity=10),
                    cls.BatchProduct(product=cls.product_b, quantity=10),
                ],
                [cls.BatchProduct(product=cls.product_a, quantity=10)],
            ]
        )
        cls.one_line_picking = cls.batch.picking_ids.filtered(
            lambda picking: len(picking.move_lines) == 1
        )
        cls.two_lines_picking = cls.batch.picking_ids.filtered(
            lambda picking: len(picking.move_lines) == 2
        )

        cls.bin1 = cls.env["stock.quant.package"].create({})
        cls.bin2 = cls.env["stock.quant.package"].create({})

        cls._simulate_batch_selected(cls.batch, in_lot=True)

    def test_scan_destination_pack_lot_missing(self):
        operation = self.batch.pack_operation_ids[0]
        next_operation = self.batch.pack_operation_ids[1]
        self.assertTrue(operation.lot_ids)
        qty_done = operation.product_qty
        response = self.service.dispatch(
            "scan_destination_pack",
            params={
                "picking_batch_id": self.batch.id,
                "operation_id": operation.id,
                "barcode": self.bin1.name,
                "quantity": qty_done,
            },
        )
        self.assert_response(
            response,
            next_state="scan_destination",
            data=self._operation_data(operation),
            message=self.service.msg_store.scan_lot_on_product_tracked_by_lot(),
        )
        lot_id = operation.lot_ids.id
        response = self.service.dispatch(
            "scan_destination_pack",
            params={
                "picking_batch_id": self.batch.id,
                "operation_id": operation.id,
                "barcode": self.bin1.name,
                "quantity": qty_done,
                "lot_id": lot_id,
            },
        )
        self.assert_response(
            response,
            next_state="start_operation",
            data=self._operation_data(next_operation),
            message={
                "message_type": "success",
                "body": "{} {} put in {}".format(
                    operation.qty_done,
                    operation.product_id.display_name,
                    self.bin1.name,
                ),
            },
        )

    def test_scan_destination_pack_lot_not_found(self):
        operation = self.batch.pack_operation_ids[0]
        self.assertTrue(operation.lot_ids)
        qty_done = operation.product_qty
        response = self.service.dispatch(
            "scan_destination_pack",
            params={
                "picking_batch_id": self.batch.id,
                "operation_id": operation.id,
                "barcode": self.bin1.name,
                "quantity": qty_done,
                "lot_id": -1,
            },
        )
        self.assert_response(
            response,
            next_state="scan_destination",
            data=self._operation_data(operation),
            message=self.service.msg_store.lot_not_found_on_operation(-1, operation.id),
        )

    def test_scan_destination_pack_lot_quantity_more(self):
        """Pick more units than expected"""
        operation = self.one_line_picking.pack_operation_ids
        lot_id = operation.lot_ids.id
        response = self.service.dispatch(
            "scan_destination_pack",
            params={
                "picking_batch_id": self.batch.id,
                "operation_id": operation.id,
                "barcode": self.bin1.name,
                "quantity": operation.product_qty + 1,
                "lot_id": lot_id,
            },
        )
        self.assert_response(
            response,
            next_state="scan_destination",
            data=self._operation_data(operation),
            message={
                "message_type": "error",
                "body": "You must not pick more than {} units.".format(
                    operation.product_qty
                ),
            },
        )

    def test_scan_destination_pack_quantity_less(self):
        """Pick less units than expected"""
        operation = self.one_line_picking.pack_operation_ids
        lot_id = operation.lot_ids.id
        quants = self.env["stock.quant"].search(
            [
                ("location_id", "=", operation.location_id.id),
                ("product_id", "=", operation.product_id.id),
            ]
        )
        self.assertEqual(20, sum(quants.mapped("qty")))
        self.assertEqual(20, sum(quants.filtered("reservation_id").mapped("qty")))

        # when we pick less quantity than expected, the line is split
        # and the user is proposed to pick the next line for the remaining
        # quantity
        response = self.service.dispatch(
            "scan_destination_pack",
            params={
                "picking_batch_id": self.batch.id,
                "operation_id": operation.id,
                "barcode": self.bin1.name,
                "quantity": operation.product_qty - 3,
                "lot_id": lot_id,
            },
        )
        new_operation = self.one_line_picking.pack_operation_ids - operation

        self.assert_response(
            response,
            next_state="start_operation",
            data=self._operation_data(new_operation),
            message={
                "message_type": "success",
                "body": "{} {} put in {}".format(
                    operation.qty_done,
                    operation.product_id.display_name,
                    self.bin1.name,
                ),
            },
        )

        self.assertRecordValues(
            operation,
            [{"qty_done": 7, "result_package_id": self.bin1.id, "product_qty": 7}],
        )
        self.assertRecordValues(
            new_operation,
            [{"qty_done": 0, "result_package_id": False, "product_qty": 3}],
        )
        self.assertEqual(new_operation.lot_ids, operation.lot_ids)
        self.assertEqual(new_operation.move_ids, operation.move_ids)
        # the reserved quantity on the quant must stay the same
        quants = self.env["stock.quant"].search(
            [
                ("location_id", "=", operation.location_id.id),
                ("product_id", "=", operation.product_id.id),
            ]
        )
        self.assertEqual(20, sum(quants.mapped("qty")))
        self.assertEqual(20, sum(quants.filtered("reservation_id").mapped("qty")))

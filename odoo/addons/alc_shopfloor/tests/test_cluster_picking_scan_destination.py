# -*- coding: utf-8 -*-
# Copyright 2020 Camptocamp SA (http://www.camptocamp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from .test_cluster_picking_base import ClusterPickingCommonCase


# pylint: disable=missing-return
class ClusterPickingScanDestinationPackCase(ClusterPickingCommonCase):
    """Tests covering the /scan_destination_pack endpoint

    After a batch has been selected and the user confirmed they are
    working on it, user picked the good, now they scan the location
    destination.
    """

    @classmethod
    def setUpClassBaseData(cls, *args, **kwargs):
        super(ClusterPickingScanDestinationPackCase, cls).setUpClassBaseData(
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

        cls._simulate_batch_selected(cls.batch)

    def test_scan_destination_pack_ok(self):
        """Happy path for scan destination package

        It sets the line in the pack for the full qty
        """
        operation = self.batch.pack_operation_ids[0]
        next_operation = self.batch.pack_operation_ids[1]
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
        self.assertRecordValues(
            operation, [{"qty_done": qty_done, "result_package_id": self.bin1.id}]
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

    def test_scan_destination_pack_ok_last_line(self):
        """Happy path for scan destination package

        It sets the line in the pack for the full qty
        """
        self._set_dest_package_and_done(
            self.one_line_picking.pack_operation_ids, self.bin1
        )
        self._set_dest_package_and_done(
            self.two_lines_picking.pack_operation_ids[0], self.bin2
        )
        # this is the only remaining line to pick
        operation = self.two_lines_picking.pack_operation_ids[1]
        qty_done = operation.product_qty
        response = self.service.dispatch(
            "scan_destination_pack",
            params={
                "picking_batch_id": self.batch.id,
                "operation_id": operation.id,
                "barcode": self.bin2.name,
                "quantity": qty_done,
            },
        )
        self.assertRecordValues(
            operation, [{"qty_done": qty_done, "result_package_id": self.bin2.id}]
        )
        data = self._data_for_batch(self.batch, self.packing_location)
        self.assert_response(
            response,
            # they reach the same destination so next state unload_all
            next_state="unload_all",
            data=data,
        )

    def test_scan_destination_pack_not_empty_same_picking(self):
        """Scan a destination package with move lines of same picking"""
        line1 = self.two_lines_picking.pack_operation_ids[0]
        line2 = self.two_lines_picking.pack_operation_ids[1]
        # we already scan and put the first line in bin1
        self._set_dest_package_and_done(line1, self.bin1)
        response = self.service.dispatch(
            "scan_destination_pack",
            params={
                "picking_batch_id": self.batch.id,
                "operation_id": line2.id,
                # this bin is used for the same picking, should be allowed
                "barcode": self.bin1.name,
                "quantity": line2.product_qty,
            },
        )
        self.assert_response(
            response,
            next_state="start_operation",
            # we did not pick this line, so it should go there
            data=self._operation_data(self.one_line_picking.pack_operation_ids),
            message=self.ANY,
        )

    def test_scan_destination_pack_not_empty_different_picking(self):
        """Scan a destination package with move lines of other picking"""
        # do as if the user already picked the first good (for another picking)
        # and put it in bin1
        self._set_dest_package_and_done(
            self.one_line_picking.pack_operation_ids, self.bin1
        )
        operation = self.two_lines_picking.pack_operation_ids[0]
        response = self.service.dispatch(
            "scan_destination_pack",
            params={
                "picking_batch_id": self.batch.id,
                "operation_id": operation.id,
                # this bin is used for the other picking
                "barcode": self.bin1.name,
                "quantity": operation.product_qty,
            },
        )
        self.assertRecordValues(
            operation, [{"qty_done": 0, "result_package_id": False}]
        )
        self.assert_response(
            response,
            next_state="scan_destination",
            data=self._operation_data(operation),
            message={
                "message_type": "error",
                "body": "The destination bin {} is not empty,"
                " please take another.".format(self.bin1.name),
            },
        )

    def test_scan_destination_pack_bin_not_found(self):
        """Scan a destination package that do not exist:
        destination package is created on the fly"""
        operation = self.batch.pack_operation_ids[0]
        next_operation = self.batch.pack_operation_ids[1]
        response = self.service.dispatch(
            "scan_destination_pack",
            params={
                "picking_batch_id": self.batch.id,
                "operation_id": operation.id,
                # this bin is used for the other picking
                "barcode": "toto",
                "quantity": operation.product_qty,
            },
        )
        self.assert_response(
            response,
            next_state="start_operation",
            data=self._operation_data(next_operation),
            message={
                "message_type": "success",
                "body": "{} {} put in {}".format(
                    operation.qty_done, operation.product_id.display_name, "toto"
                ),
            },
        )

    def test_scan_destination_pack_quantity_more(self):
        """Pick more units than expected"""
        operation = self.one_line_picking.pack_operation_ids
        response = self.service.dispatch(
            "scan_destination_pack",
            params={
                "picking_batch_id": self.batch.id,
                "operation_id": operation.id,
                "barcode": self.bin1.name,
                "quantity": operation.product_qty + 1,
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
        quants = self.env["stock.quant"].search(
            [
                ("location_id", "=", operation.location_id.id),
                ("product_id", "=", operation.product_id.id),
            ]
        )
        self.assertEqual(40, sum(quants.mapped("qty")))
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
        self.assertEqual(new_operation.move_ids, operation.move_ids)
        # the reserved quantity on the quant must stay the same
        quants = self.env["stock.quant"].search(
            [
                ("location_id", "=", operation.location_id.id),
                ("product_id", "=", operation.product_id.id),
            ]
        )
        self.assertEqual(40, sum(quants.mapped("qty")))
        self.assertEqual(20, sum(quants.filtered("reservation_id").mapped("qty")))

    def test_scan_destination_pack_zero_check_activated(self):
        """Location will be emptied, have to go to zero check"""
        # ensure that the location used for the test will contain only what we want
        self.zero_check_location = (
            self.env["stock.location"]
            .sudo()
            .create(
                {
                    "name": "ZeroCheck",
                    "location_id": self.stock_location.id,
                    "barcode": "ZEROCHECK",
                }
            )
        )
        operation = self.one_line_picking.pack_operation_ids
        location, product, qty = (
            self.zero_check_location,
            operation.product_id,
            operation.product_qty,
        )
        self.one_line_picking.do_unreserve()

        # ensure we have activated the zero check
        self.one_line_picking.picking_type_id.sudo().shopfloor_zero_check = True
        # Update the quantity in the location to be equal to the line's
        # so when scan_destination_pack sets the qty_done, the planned
        # qty should be zero and trigger a zero check
        self._update_qty_in_location(location, product, qty)
        # Reserve goods (now the move line has the expected source location)
        self.one_line_picking.move_lines.location_id = location
        self.one_line_picking.action_assign()
        operation = self.one_line_picking.pack_operation_ids
        response = self.service.dispatch(
            "scan_destination_pack",
            params={
                "picking_batch_id": self.batch.id,
                "operation_id": operation.id,
                "barcode": self.bin1.name,
                "quantity": operation.product_qty,
            },
        )

        self.assert_response(
            response,
            next_state="zero_check",
            data={
                "id": operation.id,
                "location_src": self.data.location(operation.location_id),
                "batch": self.data.picking_batch(self.batch),
            },
        )

    def test_scan_destination_pack_zero_check_disabled(self):
        """Location will be emptied, no zero check, continue"""
        operation = self.one_line_picking.pack_operation_ids
        # ensure we have deactivated the zero check
        self.one_line_picking.picking_type_id.sudo().shopfloor_zero_check = False
        # Update the quantity in the location to be equal to the line's
        # so when scan_destination_pack sets the qty_done, the planned
        # qty should be zero and trigger a zero check
        self._update_qty_in_location(
            operation.location_id, operation.product_id, operation.product_qty
        )
        response = self.service.dispatch(
            "scan_destination_pack",
            params={
                "picking_batch_id": self.batch.id,
                "operation_id": operation.id,
                "barcode": self.bin1.name,
                "quantity": operation.product_qty,
            },
        )

        next_operation = self.two_lines_picking.pack_operation_ids[0]
        # continue to the next one, no zero check
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

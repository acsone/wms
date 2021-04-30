# -*- coding: utf-8 -*-
# Copyright 2020 Camptocamp SA (http://www.camptocamp.com)
# Copyright 2021 ACSONE SA/NV (https://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from unittest import skip

from .test_location_content_transfer_base import LocationContentTransferCommonCase


# pylint: disable=missing-return
class LocationContentTransferSingleCase(LocationContentTransferCommonCase):
    """Tests for endpoint used from state start_single

    * /scan_line
    * /postpone_line

    """

    # TODO common with set_destination_all?
    @classmethod
    def setUpClassBaseData(cls, *args, **kwargs):
        super(LocationContentTransferSingleCase, cls).setUpClassBaseData(
            *args, **kwargs
        )
        products = cls.product_a + cls.product_b + cls.product_c + cls.product_d
        cls.putway = (
            cls.env["product.putaway"]
            .sudo()
            .create(
                {
                    "name": "test",
                    "method": "fixed",
                    "fixed_location_ids": [
                        (
                            0,
                            0,
                            {"category_id": c.id, "fixed_location_id": cls.shelf1.id},
                        )
                        for c in products.sudo().mapped("categ_id")
                    ],
                }
            )
        )
        cls.stock_location.sudo().putaway_strategy_id = cls.putway
        cls.product_d.tracking = "lot"
        cls.picking1 = picking1 = cls._create_picking(
            lines=[(cls.product_a, 10), (cls.product_b, 10)]
        )
        cls.picking2 = picking2 = cls._create_picking(
            lines=[(cls.product_c, 10), (cls.product_d, 10)]
        )
        cls.pickings = picking1 | picking2
        cls._fill_stock_for_moves(
            picking1.move_lines, in_package=True, location=cls.content_loc
        )
        cls.product_d_lot = cls.env["stock.production.lot"].create(
            {"product_id": cls.product_d.id}
        )
        cls._fill_stock_for_moves(picking2.move_lines[0], location=cls.content_loc)
        cls._fill_stock_for_moves(
            picking2.move_lines[1], location=cls.content_loc, in_lot=cls.product_d_lot
        )
        cls.pickings.action_assign()
        cls._simulate_pickings_selected(cls.pickings)

    def _test_scan_package_ok(self, barcode):
        pack_operation_pack = self.picking1.pack_operation_pack_ids
        response = self.service.dispatch(
            "scan_line",
            params={
                "location_id": self.content_loc.id,
                "operation_id": pack_operation_pack.id,
                "barcode": barcode,
            },
        )
        self.assert_response_scan_destination(response, pack_operation_pack)

    def test_scan_line_location_not_found(self):
        response = self.service.dispatch(
            "scan_line",
            params={
                "location_id": 1234567890,  # Doesn't exist
                "operation_id": 42,
                "barcode": "TEST",
            },
        )
        self.assert_response_start(
            response, message=self.service.msg_store.record_not_found()
        )

    def test_scan_package_package_ok(self):
        package_level = self.picking1.pack_operation_pack_ids
        self._test_scan_package_ok(package_level.package_id.name)

    def test_scan_package_barcode_not_found(self):
        package_level = self.picking1.pack_operation_pack_ids
        response = self.service.dispatch(
            "scan_line",
            params={
                "location_id": self.content_loc.id,
                "operation_id": package_level.id,
                "barcode": "NOT_FOUND",
            },
        )
        self.assert_response_start_single(
            response, self.pickings, message=self.service.msg_store.barcode_not_found()
        )

    def test_scan_package_product_ok(self):
        # product_a is in the package and anywhere else so it's
        # accepted to check we scanned the correct package
        self._test_scan_package_ok(self.product_a.barcode)

    def test_scan_package_product_packaging_ok(self):
        # product_a is in the package and anywhere else so it's
        # accepted to check we scanned the correct package
        self._test_scan_package_ok(self.product_a.packaging_ids[0].barcode)

    def test_scan_package_lot_ok(self):
        package_level = self.picking1.pack_operation_pack_ids
        self.product_a.tracking = "lot"
        quant = package_level.package_id.quant_ids.filtered(
            lambda q, p=self.product_a: q.product_id == p
        )
        quant.sudo().lot_id = self.env["stock.production.lot"].create(
            {"product_id": self.product_a.id}
        )
        # lot of product_a is in the package and anywhere else so it's
        # accepted to check we scanned the correct package
        self._test_scan_package_ok(quant.lot_id.name)

    def _test_scan_package_nok(self, pickings, barcode, message):
        package_level = self.picking1.pack_operation_pack_ids
        response = self.service.dispatch(
            "scan_line",
            params={
                "location_id": self.content_loc.id,
                "operation_id": package_level.id,
                "barcode": barcode,
            },
        )
        self.assert_response_start_single(response, pickings, message=message)

    def test_scan_package_product_nok_different_package(self):
        # add another picking with a package with product a,
        # if we scan product A, we can't know for which package it is
        picking = self._create_picking(lines=[(self.product_a, 10)])
        self._fill_stock_for_moves(
            picking.move_lines, in_package=True, location=self.content_loc
        )
        picking.action_assign()
        self._simulate_pickings_selected(picking)
        self._test_scan_package_nok(
            self.pickings | picking,
            self.product_a.barcode,
            {"message_type": "error", "body": "Scan the package"},
        )

    def test_scan_package_product_nok_different_line(self):
        # add another picking with a raw line with product a,
        # if we scan product A, we can't know which line/package we want
        picking = self._create_picking(lines=[(self.product_a, 10)])
        self._fill_stock_for_moves(picking.move_lines, location=self.content_loc)
        picking.action_assign()
        self._simulate_pickings_selected(picking)
        self._test_scan_package_nok(
            self.pickings | picking,
            self.product_a.barcode,
            {"message_type": "error", "body": "Scan the package"},
        )

    def test_scan_package_lot_nok_different_package(self):
        # add another picking with a package with the lot used in our package,
        # if we scan the lot, we can't know for which package it is
        package_level = self.picking1.pack_operation_pack_ids
        self.product_a.tracking = "lot"
        quant = package_level.package_id.quant_ids.filtered(
            lambda q, p=self.product_a: q.product_id == p
        )
        quant.sudo().lot_id = lot = self.env["stock.production.lot"].create(
            {"product_id": self.product_a.id}
        )
        picking = self._create_picking(lines=[(self.product_a, 10)])
        self._fill_stock_for_moves(
            picking.move_lines, in_package=True, in_lot=lot, location=self.content_loc
        )
        picking.action_assign()
        self._simulate_pickings_selected(picking)
        self._test_scan_package_nok(
            self.pickings | picking,
            self.product_a.barcode,
            {"message_type": "error", "body": "Scan the package"},
        )

    def test_scan_package_lot_nok_different_line(self):
        # add another picking with a raw line with a lot used in our package,
        # if we scan the lot, we can't know which line/package we want
        package_level = self.picking1.pack_operation_pack_ids
        self.product_a.tracking = "lot"
        quant = package_level.package_id.quant_ids.filtered(
            lambda q, p=self.product_a: q.product_id == p
        )
        quant.sudo().lot_id = lot = self.env["stock.production.lot"].create(
            {"product_id": self.product_a.id}
        )
        picking = self._create_picking(lines=[(self.product_a, 10)])
        self._fill_stock_for_moves(
            picking.move_lines, in_lot=lot, location=self.content_loc
        )
        picking.action_assign()
        self._simulate_pickings_selected(picking)
        self._test_scan_package_nok(
            self.pickings | picking,
            self.product_a.barcode,
            {"message_type": "error", "body": "Scan the package"},
        )

    def test_scan_package_package_level_not_exists(self):
        package_level = self.picking1.pack_operation_pack_ids
        operation_id = package_level.id
        package_level.unlink()
        response = self.service.dispatch(
            "scan_line",
            params={
                "location_id": self.content_loc.id,
                "operation_id": operation_id,
                "barcode": self.product_a.barcode,
            },
        )
        self.assert_response_start_single(
            response, self.pickings, message=self.service.msg_store.record_not_found()
        )

    def _test_scan_line_ok(self, move_line, barcode):
        response = self.service.dispatch(
            "scan_line",
            params={
                "location_id": self.content_loc.id,
                "operation_id": move_line.id,
                "barcode": barcode,
            },
        )
        self.assert_response_scan_destination(response, move_line)

    def test_scan_line_package_ok(self):
        operation = self.picking2.pack_operation_product_ids[0]
        package = operation.package_id = self.env["stock.quant.package"].create({})
        self._test_scan_line_ok(operation, package.name)

    def test_scan_line_product_ok(self):
        operation = self.picking2.pack_operation_product_ids[0]
        # check we selected the good line
        self.assertEqual(operation.product_id, self.product_c)
        self._test_scan_line_ok(operation, self.product_c.barcode)

    def test_scan_line_product_packaging_ok(self):
        operation = self.picking2.pack_operation_product_ids[0]
        # check we selected the good line
        self.assertEqual(operation.product_id, self.product_c)
        self._test_scan_line_ok(operation, self.product_c.packaging_ids[0].barcode)

    def test_scan_line_lot_ok(self):
        operation = self.picking2.pack_operation_product_ids[1]
        # check we selected the good line (the one with a lot)
        self.assertEqual(operation.product_id, self.product_d)
        self._test_scan_line_ok(operation, self.product_d_lot.name)

    def _test_scan_line_nok(self, pickings, operation_id, barcode, message):
        response = self.service.dispatch(
            "scan_line",
            params={
                "location_id": self.content_loc.id,
                "operation_id": operation_id,
                "barcode": barcode,
            },
        )
        self.assert_response_start_single(response, pickings, message=message)

    def test_scan_line_product_nok_product_tracked(self):
        # we scan product_d's barcode but it's tracked by lot
        operation = self.picking2.pack_operation_product_ids[1]
        # check we selected the good line (the one with a lot)
        self.assertEqual(operation.product_id, self.product_d)
        self._test_scan_line_nok(
            self.pickings,
            operation.id,
            self.product_d.barcode,
            self.service.msg_store.scan_lot_on_product_tracked_by_lot(),
        )

    def test_scan_line_barcode_not_found(self):
        operation = self.picking2.pack_operation_product_ids[0]
        self._test_scan_line_nok(
            self.pickings,
            operation.id,
            "NOT_FOUND",
            self.service.msg_store.barcode_not_found(),
        )

    def test_scan_line_move_line_not_exists(self):
        operation = self.picking2.pack_operation_product_ids[0]
        operation_id = operation.id
        operation.unlink()
        self._test_scan_line_nok(
            self.pickings,
            operation_id,
            "NOT_FOUND",
            self.service.msg_store.record_not_found(),
        )

    def test_postpone_package_wrong_parameters(self):
        """Wrong 'location_id' and 'package_level_id' parameters, redirect the
        user to the 'start' screen.
        """
        package_level = self.picking1.pack_operation_pack_ids
        response = self.service.dispatch(
            "postpone_line",
            params={
                "location_id": 1234567890,  # Doesn't exist
                "operation_id": package_level.id,
            },
        )
        self.assert_response_start(
            response, message=self.service.msg_store.record_not_found()
        )
        response = self.service.dispatch(
            "postpone_line",
            params={
                "location_id": self.content_loc.id,
                "operation_id": 1234567890,  # Doesn't exist
            },
        )
        operations = self.service._find_operations(self.content_loc)
        self.assert_response_start_single(
            response, operations.mapped("picking_id"),
        )

    def test_postpone_package_ok(self):
        package_level = self.picking1.pack_operation_pack_ids
        previous_priority = package_level.shopfloor_priority
        self.assertFalse(package_level.shopfloor_postponed)
        response = self.service.dispatch(
            "postpone_line",
            params={
                "location_id": self.content_loc.id,
                "operation_id": package_level.id,
            },
        )
        self.assertTrue(package_level.shopfloor_postponed)
        self.assertEqual(package_level.shopfloor_priority, previous_priority + 1)
        operations = self.service._find_operations(self.content_loc)
        self.assert_response_start_single(
            response, operations.mapped("picking_id"),
        )

    def test_postpone_sorter(self):
        operation = self.picking2.pack_operation_product_ids[0]
        operations = self.service._find_operations(self.content_loc)
        pickings = operations.mapped("picking_id")
        sorter = self.service._actions_for("location_content_transfer.sorter")
        sorter.feed_pickings(pickings)
        content_sorted1 = list(sorter)
        self.service.dispatch(
            "postpone_line",
            params={"location_id": self.content_loc.id, "operation_id": operation.id},
        )
        sorter.sort()
        content_sorted2 = list(sorter)
        self.assertTrue(content_sorted1 != content_sorted2)

    def test_postpone_line_wrong_parameters(self):
        """Wrong 'location_id' and 'move_line_id' parameters, redirect the
        user to the 'start' screen.
        """
        operation = self.picking2.pack_operation_product_ids[0]
        response = self.service.dispatch(
            "postpone_line",
            params={
                "location_id": 1234567890,  # Doesn't exist
                "operation_id": operation.id,
            },
        )
        self.assert_response_start(
            response, message=self.service.msg_store.record_not_found()
        )
        response = self.service.dispatch(
            "postpone_line",
            params={
                "location_id": self.content_loc.id,
                "operation_id": 1234567890,  # Doesn't exist
            },
        )
        operations = self.service._find_operations(self.content_loc)
        self.assert_response_start_single(
            response, operations.mapped("picking_id"),
        )

    def test_postpone_line_ok(self):
        operation = self.picking2.pack_operation_product_ids[0]
        previous_priority = operation.shopfloor_priority
        self.assertFalse(operation.shopfloor_postponed)
        response = self.service.dispatch(
            "postpone_line",
            params={"location_id": self.content_loc.id, "operation_id": operation.id},
        )
        self.assertTrue(operation.shopfloor_postponed)
        self.assertEqual(operation.shopfloor_priority, previous_priority + 1)
        operations = self.service._find_operations(self.content_loc)
        self.assert_response_start_single(
            response, operations.mapped("picking_id"),
        )

    @skip("Not yet implemented")
    def test_stock_out_package_wrong_parameters(self):
        """Wrong 'location_id' and 'package_level_id' parameters, redirect the
        user to the 'start' screen.
        """
        package_level = self.picking1.pack_operation_pack_ids
        response = self.service.dispatch(
            "stock_out_package",
            params={
                "location_id": 1234567890,  # Doesn't exist
                "operation_id": package_level.id,
            },
        )
        self.assert_response_start(
            response, message=self.service.msg_store.record_not_found()
        )
        response = self.service.dispatch(
            "stock_out_package",
            params={
                "location_id": self.content_loc.id,
                "operation_id": 1234567890,  # Doesn't exist
            },
        )
        operations = self.service._find_operations(self.content_loc)
        self.assert_response_start_single(
            response, operations.mapped("picking_id"),
        )

    @skip("Not yet implemented")
    def test_stock_out_package_ok(self):
        """Declare a stock out on a package_level."""
        package_level = self.picking1.pack_operation_pack_ids
        response = self.service.dispatch(
            "stock_out_package",
            params={
                "location_id": self.content_loc.id,
                "operation_id": package_level.id,
            },
        )
        operations = self.service._find_operations(self.content_loc)
        self.assert_response_start_single(
            response, operations.mapped("picking_id"),
        )

    @skip("Not yet implemented")
    def test_stock_out_line_wrong_parameters(self):
        """Wrong 'location_id' and 'move_line_id' parameters, redirect the
        user to the 'start' screen.
        """
        move_line = self.picking2.pack_operation_product_ids[0]
        response = self.service.dispatch(
            "stock_out_line",
            params={
                "location_id": 1234567890,  # Doesn't exist
                "operation_id": move_line.id,
            },
        )
        self.assert_response_start(
            response, message=self.service.msg_store.record_not_found()
        )
        response = self.service.dispatch(
            "stock_out_line",
            params={
                "location_id": self.content_loc.id,
                "operation_id": 1234567890,  # Doesn't exist
            },
        )
        operations = self.service._find_operations(self.content_loc)
        self.assert_response_start_single(
            response, operations.mapped("picking_id"),
        )


# pylint: disable=missing-return
class LocationContentTransferSingleSpecialCase(LocationContentTransferCommonCase):
    """Tests for endpoint used from state start_single (special cases)

    * /stock_out_line

    """

    @classmethod
    def setUpClassBaseData(cls, *args, **kwargs):
        super(LocationContentTransferSingleSpecialCase, cls).setUpClassBaseData(
            *args, **kwargs
        )
        products = cls.product_a | cls.product_b
        cls.putway = (
            cls.env["product.putaway"]
            .sudo()
            .create(
                {
                    "name": "test",
                    "method": "fixed",
                    "fixed_location_ids": [
                        (
                            0,
                            0,
                            {"category_id": c.id, "fixed_location_id": cls.shelf1.id},
                        )
                        for c in products.sudo().mapped("categ_id")
                    ],
                }
            )
        )
        cls.stock_location.sudo().putaway_strategy_id = cls.putway
        cls.picking = cls._create_picking(
            lines=[(cls.product_a, 10), (cls.product_b, 10)]
        )
        cls.move_product_a = cls.picking.move_lines.filtered(
            lambda m: m.product_id == cls.product_a
        )
        cls.move_product_b = cls.picking.move_lines.filtered(
            lambda m: m.product_id == cls.product_b
        )
        # Change the initial demand of product_a to get two move lines for
        # reserved qties:
        #   - 10 from the package
        #   - 5 from the qty without package
        cls._fill_stock_for_moves(
            cls.move_product_a, in_package=True, location=cls.content_loc
        )
        cls.move_product_a.product_uom_qty = 15
        cls._update_qty_in_location(
            cls.content_loc, cls.product_a, 5,
        )
        # Put product_b quantities in two different source locations to get
        # two stock move lines (6 and 4 to satisfy 10 qties)
        cls._update_qty_in_location(cls.picking.location_id, cls.product_b, 6)
        cls._update_qty_in_location(cls.content_loc, cls.product_b, 4)
        # Reserve quantities
        cls.picking.action_assign()
        cls._simulate_pickings_selected(cls.picking)

    @skip("Not yet implemented")
    def test_stock_out_package_split_move(self):
        """Declare a stock out on a package_level related to moves containing
        other unrelated move lines.
        """
        package_level = self.picking.move_line_ids.package_level_id
        self.assertEqual(self.product_a.qty_available, 15)
        response = self.service.dispatch(
            "stock_out_package",
            params={
                "location_id": self.content_loc.id,
                "operation_id": package_level.id,
            },
        )
        # Check the picking data
        self.assertFalse(package_level.exists())
        moves_product_a = self.picking.move_lines.filtered(
            lambda m: m.product_id == self.product_a
        )
        self.assertEqual(len(moves_product_a), 2)
        move_product_a = moves_product_a.filtered(
            lambda m: m.state not in ("cancel", "done")
        )
        self.assertEqual(len(move_product_a), 1)
        self.assertEqual(move_product_a.state, "assigned")
        self.assertEqual(len(move_product_a.move_line_ids), 1)
        # Check the inventories
        stock_issue_inventory = self.env["stock.inventory"].search(
            [
                ("line_ids.location_id", "=", self.content_loc.id),
                ("line_ids.product_id", "=", self.product_a.id),
                ("state", "=", "done"),
            ]
        )
        self.assertTrue(stock_issue_inventory)
        stock_issue_inventory_line = stock_issue_inventory.line_ids.filtered(
            lambda l: l.product_id == self.product_a
        )
        #   5/15 remaining
        self.assertEqual(stock_issue_inventory_line.product_qty, 0)
        self.assertEqual(self.product_a.qty_available, 5)
        control_inventory = self.env["stock.inventory"].search(
            [
                ("location_ids", "in", self.content_loc.id),
                ("product_ids", "in", self.product_a.id),
                ("state", "in", ("draft", "confirm")),
            ]
        )
        self.assertTrue(control_inventory)
        # Check the response
        operations = self.service._find_operations(self.content_loc)
        self.assert_response_start_single(
            response, operations.mapped("picking_id"),
        )

    @skip("Not yet implemented")
    def test_stock_out_line_split_move(self):
        """Declare a stock out on a move line related to moves containing
        other move lines.
        """
        self.assertEqual(len(self.picking.move_lines), 2)
        self.assertEqual(len(self.move_product_b.move_line_ids), 2)
        move_line = self.move_product_b.move_line_ids.filtered(
            lambda ml: ml.product_uom_qty == 4  # 4/10 to stock out
        )
        self.assertEqual(self.product_b.qty_available, 10)
        response = self.service.dispatch(
            "stock_out_line",
            params={"location_id": self.content_loc.id, "operation_id": move_line.id},
        )
        # Check the picking data
        self.assertFalse(move_line.exists())
        moves_product_b = self.picking.move_lines.filtered(
            lambda m: m.product_id == self.product_b
        )
        self.assertEqual(len(moves_product_b), 2)
        move_product_b = moves_product_b.filtered(
            lambda m: m.state not in ("cancel", "done")
        )
        self.assertEqual(len(move_product_b), 1)
        self.assertEqual(move_product_b.state, "assigned")
        self.assertEqual(len(move_product_b.move_line_ids), 1)
        # Check the inventories
        stock_issue_inventory = self.env["stock.inventory"].search(
            [
                ("line_ids.location_id", "=", self.content_loc.id),
                ("line_ids.product_id", "=", self.product_b.id),
                ("state", "=", "done"),
            ]
        )
        self.assertTrue(stock_issue_inventory)
        stock_issue_inventory_line = stock_issue_inventory.line_ids.filtered(
            lambda l: l.product_id == self.product_b
        )
        #   0/4 remaining in the move line's source location
        self.assertEqual(stock_issue_inventory_line.product_qty, 0)
        #   6/10 remaining elsewhere in the stock
        self.assertEqual(self.product_b.qty_available, 6)
        control_inventory = self.env["stock.inventory"].search(
            [
                ("location_ids", "in", self.content_loc.id),
                ("product_ids", "in", self.product_b.id),
                ("state", "in", ("draft", "confirm")),
            ]
        )
        self.assertTrue(control_inventory)
        # Check the response
        operations = self.service._find_operations(self.content_loc)
        self.assert_response_start_single(
            response, operations.mapped("picking_id"),
        )

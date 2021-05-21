# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV (https://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from .test_location_content_transfer_base import LocationContentTransferCommonCase


# pylint: disable=missing-return
class LocationContentTransferSetDestinationXCase(LocationContentTransferCommonCase):
    """Tests for endpoint used from scan_destination with lot

    * /set_destination_line

    """

    # TODO see what can be common
    @classmethod
    def setUpClassBaseData(cls, *args, **kwargs):
        super(LocationContentTransferSetDestinationXCase, cls).setUpClassBaseData(
            *args, **kwargs
        )
        products = cls.product_a + cls.product_b + cls.product_c
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

        cls.product_a.tracking = "lot"
        cls.product_b.tracking = "lot"
        cls.product_c.tracking = "lot"

        # First picking:
        # Product A -> 1 lot, 1 move
        # Product B -> 2 lots, 1 move
        cls.picking = picking = cls._create_picking(
            lines=[(cls.product_a, 10), (cls.product_b, 10)]
        )

        cls.product_a_lot = cls.env["stock.production.lot"].create(
            {"product_id": cls.product_a.id}
        )
        cls.product_b_lot_1 = cls.env["stock.production.lot"].create(
            {"product_id": cls.product_b.id}
        )
        cls.product_b_lot_2 = cls.env["stock.production.lot"].create(
            {"product_id": cls.product_b.id}
        )

        cls._fill_stock_for_moves(
            picking.move_lines[0], location=cls.content_loc, in_lot=cls.product_a_lot
        )

        cls._update_qty_in_location(
            cls.content_loc, cls.product_b, 5, lot=cls.product_b_lot_1
        )
        cls._update_qty_in_location(
            cls.content_loc, cls.product_b, 5, lot=cls.product_b_lot_2
        )
        cls._fill_stock_for_moves(
            picking.move_lines, in_package=True, location=cls.content_loc
        )

        cls.picking.action_assign()

        cls.dest_location = cls.shelf1

        # Second picking:
        # Product C -> 1 lot, 2 moves
        cls.picking2 = picking2 = cls._create_picking(
            lines=[(cls.product_c, 4), (cls.product_c, 6)]
        )

        cls.product_c_lot = cls.env["stock.production.lot"].create(
            {"product_id": cls.product_c.id}
        )

        cls._update_qty_in_location(
            cls.content_loc, cls.product_c, 4, lot=cls.product_c_lot
        )
        # create an other quant for the same lot
        cls.env["stock.quant"].sudo().create(
            {
                "product_id": cls.product_c.id,
                "location_id": cls.content_loc.id,
                "qty": 6,
                "lot_id": cls.product_c_lot.id,
                "in_date": "2021 01 02",
            }
        )
        cls._fill_stock_for_moves(
            picking2.move_lines, in_package=True, location=cls.content_loc
        )

        cls.picking2.action_assign()

    def test_set_destination_all_with_lot(self):
        """ lot_id parameter not st, redirect the
        user to the 'start' screen.
        """
        self._simulate_pickings_selected(self.picking)
        response = self.service.dispatch(
            "set_destination_all",
            params={
                "location_id": self.content_loc.id,
                "barcode": self.dest_location.barcode,
            },
        )
        self.assert_response_start(
            response,
            message=self.service.msg_store.location_content_transfer_complete(
                self.content_loc, self.dest_location
            ),
        )
        self.assertRecordValues(
            self.picking.mapped("pack_operation_product_ids"),
            [
                {
                    "qty_done": 10.0,
                    "state": "done",
                    "location_dest_id": self.dest_location.id,
                },
                {
                    "qty_done": 10.0,
                    "state": "done",
                    "location_dest_id": self.dest_location.id,
                },
            ],
        )
        self.assertEqual(self.picking.state, "done")

        quants = self.env["stock.quant"].search(
            [
                ("location_id", "=", self.dest_location.id),
                (
                    "lot_id",
                    "in",
                    [
                        self.product_a_lot.id,
                        self.product_b_lot_1.id,
                        self.product_b_lot_2.id,
                    ],
                ),
            ]
        )
        self.assertEqual(3, len(quants))

    def test_set_destination_line_missing_lot(self):
        """ lot_id parameter not st, redirect the
        user to the 'start' screen.
        """
        self._simulate_pickings_selected(self.picking)
        pack_lot_a = self.picking.pack_operation_product_ids[0]
        response = self.service.dispatch(
            "set_destination_line",
            params={
                "location_id": self.content_loc.id,
                "operation_id": pack_lot_a.id,
                "barcode": self.dest_location.barcode,
                "quantity": pack_lot_a.product_qty,
            },
        )
        self.assert_response_start_single(
            response,
            self.picking,
            message=self.service.msg_store.scan_lot_on_product_tracked_by_lot(),
        )

    def test_set_destination_line_lot(self):
        """ Execute the operation linked to 1 lot.
        The operation should be complete
        """
        self._simulate_pickings_selected(self.picking)
        pack_lot_a = self.picking.pack_operation_product_ids[0]
        move = pack_lot_a.linked_move_operation_ids.move_id
        response = self.service.dispatch(
            "set_destination_line",
            params={
                "location_id": self.content_loc.id,
                "operation_id": pack_lot_a.id,
                "barcode": self.dest_location.barcode,
                "quantity": pack_lot_a.product_qty,
                "lot_id": self.product_a_lot.id,
            },
        )
        self.assertEqual(move.state, "done")
        self.assertEqual(move.picking_id.state, "done")
        self.assertEqual(self.picking.backorder_ids, move.picking_id)
        operations = self.service._find_operations(self.content_loc)
        completion_info = self.service._actions_for("completion.info")
        completion_info_popup = completion_info.popup(move)
        self.assert_response_start_single(
            response,
            operations.mapped("picking_id"),
            message=self.service.msg_store.location_content_transfer_item_complete(
                self.dest_location
            ),
            popup=completion_info_popup,
        )
        self.assertEqual(self.picking.state, "assigned")
        remaining_operation = self.picking.pack_operation_product_ids
        self.assertEqual(len(remaining_operation), 1)
        self.assertEqual(remaining_operation.product_id, self.product_b)
        self.assertEqual(remaining_operation.state, "assigned")

    def test_set_destination_line_lot_one_of_two(self):
        """ Execute the operation linked to 2 lots for the first lot.
        A new operation must be created for the second lot.
        """
        self._simulate_pickings_selected(self.picking)
        pack_lot_b = self.picking.pack_operation_product_ids[1]
        move = pack_lot_b.linked_move_operation_ids.move_id
        response = self.service.dispatch(
            "set_destination_line",
            params={
                "location_id": self.content_loc.id,
                "operation_id": pack_lot_b.id,
                "barcode": self.dest_location.barcode,
                "quantity": 5,
                "lot_id": self.product_b_lot_1.id,
            },
        )
        # the operation should be linked to a new move with only 1 pack_lot
        move_done = pack_lot_b.linked_move_operation_ids.move_id
        self.assertNotEqual(move, move_done)
        self.assertEqual(move_done.state, "done")
        self.assertEqual(move_done.picking_id.state, "done")
        self.assertEqual(pack_lot_b.pack_lot_ids.lot_id, self.product_b_lot_1)
        # the move must be assigned with the remaining lot
        self.assertEqual(move.state, "assigned")
        self.assertEqual(move.picking_id.state, "assigned")
        self.assertEqual(
            move.pack_operation_ids.pack_lot_ids.lot_id, self.product_b_lot_2
        )

        # the response should be a transfer complete for the current operation
        operations = self.service._find_operations(self.content_loc)
        completion_info = self.service._actions_for("completion.info")
        completion_info_popup = completion_info.popup(move)
        self.assert_response_start_single(
            response,
            operations.mapped("picking_id"),
            message=self.service.msg_store.location_content_transfer_item_complete(
                self.dest_location
            ),
            popup=completion_info_popup,
        )

        remaining_operation = self.picking.pack_operation_product_ids
        self.assertEqual(len(remaining_operation), 2)
        self.assertEqual(
            remaining_operation.mapped("product_id"), self.product_a | self.product_b
        )
        self.assertEqual(set(remaining_operation.mapped("state")), {"assigned"})

        # process remaining operation
        operation = self.picking.pack_operation_product_ids
        while operation:
            operation = operation[0]
            self.service.dispatch(
                "set_destination_line",
                params={
                    "location_id": self.content_loc.id,
                    "operation_id": operation.id,
                    "barcode": self.dest_location.barcode,
                    "quantity": operation.pack_lot_ids.qty_todo,
                    "lot_id": operation.pack_lot_ids.lot_id.id,
                },
            )
            operation = self.picking.pack_operation_product_ids.filtered(
                lambda op: op.state == "assigned"
            )

        self.assertEqual(self.picking.state, "done")

    def test_set_destination_line_lot_same_lot_two_move(self):
        """ Execute an operation for the same lot linked to 2 moves
        The 2 moves must be done
        """
        self._simulate_pickings_selected(self.picking2)
        self.assertEqual(2, len(self.picking2.move_lines))
        self.assertEqual(1, len(self.picking2.pack_operation_ids))
        pack_lot = self.picking2.pack_operation_product_ids
        moves = pack_lot.mapped("linked_move_operation_ids.move_id")
        response = self.service.dispatch(
            "set_destination_line",
            params={
                "location_id": self.content_loc.id,
                "operation_id": pack_lot.id,
                "barcode": self.dest_location.barcode,
                "quantity": 10,
                "lot_id": self.product_c_lot.id,
            },
        )
        # all the moves are done
        self.assertEqual(["done", "done"], moves.mapped("state"))
        # The picking should be complete
        self.assertEqual("done", self.picking2.state)

        self.assert_response_start(
            response,
            message=self.service.msg_store.location_content_transfer_item_complete(
                self.dest_location
            ),
        )

    def test_set_destination_line_lot_partial(self):
        """ Execute partially the operation linked to 1 lot.
        The operation should be split and a new operation should be created
        for the same lot with the remaining qty
        """
        self._simulate_pickings_selected(self.picking)
        pack_lot_a = self.picking.pack_operation_product_ids[0]
        move = pack_lot_a.linked_move_operation_ids.move_id
        response = self.service.dispatch(
            "set_destination_line",
            params={
                "location_id": self.content_loc.id,
                "operation_id": pack_lot_a.id,
                "barcode": self.dest_location.barcode,
                "quantity": pack_lot_a.product_qty - 2,
                "lot_id": self.product_a_lot.id,
            },
        )
        move_done = pack_lot_a.linked_move_operation_ids.move_id
        self.assertNotEqual(move, move_done)
        self.assertEqual(move_done.state, "done")
        self.assertEqual(move_done.picking_id.state, "done")
        self.assertEqual(self.picking.backorder_ids, move_done.picking_id)
        operations = self.service._find_operations(self.content_loc)
        completion_info = self.service._actions_for("completion.info")
        completion_info_popup = completion_info.popup(move)
        self.assert_response_start_single(
            response,
            operations.mapped("picking_id"),
            message=self.service.msg_store.location_content_transfer_item_complete(
                self.dest_location
            ),
            popup=completion_info_popup,
        )
        self.assertEqual(move.state, "assigned")
        self.assertEqual(move.picking_id.state, "assigned")
        self.assertEqual(move.reserved_quant_ids.lot_id, self.product_a_lot)
        remaining_operation = self.picking.pack_operation_product_ids
        self.assertEqual(len(remaining_operation), 2)
        pack_lot_a = self.picking.pack_operation_product_ids.filtered(
            lambda op, p=self.product_a: op.product_id == p
        )
        self.assertTrue(pack_lot_a)
        self.assertEqual(pack_lot_a.product_qty, 2)
        self.assertEqual(pack_lot_a.pack_lot_ids.lot_id, self.product_a_lot)
        self.assertEqual(pack_lot_a.state, "assigned")

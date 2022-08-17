# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.alc_shopfloor.tests.test_location_content_transfer_base import (
    LocationContentTransferCommonCase,
)


class TestLocationContentTransferReserve(LocationContentTransferCommonCase):
    @classmethod
    def setUpClass(cls):
        super(TestLocationContentTransferReserve, cls).setUpClass()
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
        cls.reserve = (
            cls.env["stock.location"]
            .sudo()
            .create(
                {
                    "kind": "reserve",
                    "location_id": cls.stock_location.id,
                    "name": "Stock Reserve",
                }
            )
        )
        cls.picking1 = cls._create_picking(
            lines=[(cls.product_a, 10), (cls.product_b, 10)]
        )

        cls.picking2 = cls._create_picking(
            lines=[(cls.product_c, 10), (cls.product_d, 10)]
        )
        cls.pickings = cls.picking1 | cls.picking2
        cls._fill_stock_for_moves(
            cls.picking1.move_lines, in_package=True, location=cls.content_loc
        )
        cls.product_d_lot = cls.env["stock.production.lot"].create(
            {"product_id": cls.product_d.id}
        )
        cls._fill_stock_for_moves(cls.picking2.move_lines[0], location=cls.content_loc)
        cls._fill_stock_for_moves(
            cls.picking2.move_lines[1],
            location=cls.content_loc,
            in_lot=cls.product_d_lot,
        )
        cls.pickings.action_assign()
        cls._simulate_pickings_selected(cls.pickings)

    def test_overstock_line_wrong_parameters(self):
        """Wrong 'location_id' and 'operation_id' parameters, redirect the
        user to the 'start' screen.
        """
        operation = self.picking1.pack_operation_pack_ids
        response = self.service.dispatch(
            "overstock_line",
            params={
                "location_id": 1234567890,  # Doesn't exist
                "operation_id": operation.id,
            },
        )
        self.assert_response_start(
            response, message=self.service.msg_store.record_not_found()
        )
        response = self.service.dispatch(
            "overstock_line",
            params={
                "location_id": self.content_loc.id,
                "operation_id": 1234567890,  # Doesn't exist
            },
        )
        operations = self.service._find_operations(self.content_loc)
        self.assert_response_start_single(
            response,
            operations.mapped("picking_id"),
            message=self.service.msg_store.record_not_found(),
        )

    def test_overstock_line_ok(self):
        """Declare an overstock on an operation. The process should return
        a new operation to a reserve location
        """
        self.shelf1.sudo().reserve_location_id = self.reserve
        operation = self.picking1.pack_operation_pack_ids

        response = self.service.dispatch(
            "overstock_line",
            params={
                "location_id": operation.location_dest_id.id,
                "operation_id": operation.id,
            },
        )
        self.assertIn("start_single", response["data"])
        data_operation = response["data"]["start_single"]["operation"]
        self.assertEqual(self.reserve.id, data_operation["location_dest"]["id"])
        moves = operation.linked_move_operation_ids.mapped("move_id")
        self.assertEqual(self.reserve, moves.mapped("location_dest_id"))
        self.assertEqual({"assigned"}, set(moves.mapped("state")))

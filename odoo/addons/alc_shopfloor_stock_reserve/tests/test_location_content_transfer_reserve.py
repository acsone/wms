# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.shopfloor.tests.test_location_content_transfer_base import (
    LocationContentTransferCommonCase,
)


class TestLocationContentTransferReserve(LocationContentTransferCommonCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        products = cls.product_a + cls.product_b + cls.product_c + cls.product_d
        cls.picking1 = cls._create_picking(
            lines=[(cls.product_a, 10), (cls.product_b, 10)]
        )

        cls.picking2 = cls._create_picking(
            lines=[(cls.product_c, 10), (cls.product_d, 10)]
        )
        cls.pickings = cls.picking1 | cls.picking2
        cls._fill_stock_for_moves(
            cls.picking1.move_ids, in_package=True, location=cls.content_loc
        )
        cls.product_d_lot = cls.env["stock.lot"].create(
            {"product_id": cls.product_d.id}
        )
        cls._fill_stock_for_moves(cls.picking2.move_ids[0], location=cls.content_loc)
        cls._fill_stock_for_moves(
            cls.picking2.move_ids[1],
            location=cls.content_loc,
            in_lot=cls.product_d_lot,
        )
        cls.pickings.action_assign()
        cls._simulate_pickings_selected(cls.pickings)
        putaway_rule_model = cls.env["stock.putaway.rule"].sudo()
        cls.reserve = (
            cls.env["stock.location"]
            .sudo()
            .create({"location_id": cls.stock_location.id, "name": "Stock Reserve"})
        )
        for product in products:
            putaway_rule_model.create(
                {
                    "location_in_id": cls.stock_location.id,
                    "location_out_id": cls.reserve.id,
                    "product_id": product.id,
                }
            )

    def test_overstock_line_wrong_parameters(self):
        """Wrong 'location_id' and 'move_line_id' parameters, redirect the.

        user to the 'start' screen.
        """
        move_line = self.picking1.move_line_ids[0]
        response = self.service.dispatch(
            "overstock_line",
            params={
                "location_id": 1234567890,  # Doesn't exist
                "move_line_id": move_line.id,
            },
        )
        self.assertDictEqual(
            response.get("message"), self.service.msg_store.record_not_found()
        )
        response = self.service.dispatch(
            "overstock_line",
            params={
                "location_id": self.content_loc.id,
                "move_line_id": 1234567890,  # Doesn't exist
            },
        )
        self.assertDictEqual(
            response.get("message"), self.service.msg_store.record_not_found()
        )

    def test_overstock_line_ok(self):
        """Declare an overstock on an operation.

        The process should return
        a new operation to a reserve location
        """
        move_line = self.picking1.move_line_ids[0]

        response = self.service.dispatch(
            "overstock_line",
            params={
                "location_id": move_line.location_dest_id.id,
                "move_line_id": move_line.id,
            },
        )
        self.assertIn("start_single", response["data"])
        data_move_line = response["data"]["start_single"]["move_line"]
        self.assertEqual(self.reserve.id, data_move_line["location_dest"]["id"])
        move = move_line.move_id
        self.assertEqual(self.reserve, move_line.location_dest_id)
        self.assertEqual(self.reserve, move.location_dest_id)
        self.assertEqual("assigned", move.state)

# Copyright 2023 Michael Tietz (MT Software) <mtietz@mt-software.de>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.shopfloor.tests.test_location_content_transfer_base import (
    LocationContentTransferCommonCase,
)
from odoo.addons.stock_location_orderpoint.tests.common import (
    TestLocationOrderpointCommon,
)


class LocationContentTransferFull(
    LocationContentTransferCommonCase, TestLocationOrderpointCommon
):
    """Tests for Stock Content Transfer in Full Reservation context."""

    @classmethod
    def setUpClassBaseData(cls):
        res = super().setUpClassBaseData()
        cls.env = cls.env(context=dict(cls.env.context, queue_job__no_delay=True))
        # Save user
        user = cls.env.user
        cls.env = cls.env(user=1)
        cls.picking_type_out = cls.env.ref("stock.picking_type_out")
        orderpoint, location_src = cls._create_orderpoint_complete(
            "Reserve", trigger="auto"
        )
        cls.reserve_picking_type = orderpoint.route_id.rule_ids.picking_type_id
        cls.reserve_picking_type.merge_move_for_full_location_reservation = True
        # Update shopfloor profile picking types
        cls.menu.sudo().picking_type_ids = orderpoint.route_id.rule_ids.picking_type_id

        cls.reserve = location_src

        cls.location_obj = cls.env["stock.location"]
        cls.location_reserve_1 = cls.location_obj.create(
            {
                "name": "Reserve 1",
                "location_id": location_src.id,
                "barcode": "RESERVE1",
            }
        )
        cls.location_reserve_2 = cls.location_obj.create(
            {
                "name": "Reserve 2",
                "location_id": location_src.id,
                "barcode": "RESERVE2",
            }
        )

        cls._update_qty_in_location(cls.location_reserve_1, cls.product_a, 10)
        cls._update_qty_in_location(cls.location_reserve_2, cls.product_a, 10)

        cls.picking = cls._create_picking(
            picking_type=cls.picking_type_out, lines=[(cls.product_a, 20)]
        )
        cls.picking.picking_type_id.merge_move_for_full_location_reservation = True
        # We don't treat the remaining quantities
        cls.picking.picking_type_id.create_backorder = "never"

        # Reserve quantities
        cls.picking.action_assign()

        cls.env = cls.env(user=user.id)
        return res

    def test_scan_location_assignation_partial_inferior(self):
        """
        Test case:

            We will try to do an inferior quantity than the needed quantities
            to refill the actual demand.

            - Product A is present in several sub location of 'Stock':

                - Sub location 1: 10.0
                - Sub location 2: 10.0

            - Create a picking of 20.0 from Stock
            - Refill the Stock of Product A with 30.0
            - Launch the refill through Shopfloor
            - Refill only 15.0 quantities

            - Shopfloor should present the 5.0 remaining quantities
        """
        self.menu.sudo().full_location_reservation = True
        self.menu.sudo().allow_get_work = True

        # Refill one location
        self._update_qty_in_location(self.location_reserve_1, self.product_a, 30)

        # Search for Refill picking
        refill_moves = self.env["stock.move"].search(
            [("location_id", "=", self.reserve.id)]
        )

        # Check two lines have been created for one move
        self.assertEqual(1, len(refill_moves))
        self.assertEqual(2, len(refill_moves.move_line_ids))

        res = self.service.dispatch("find_work", params={})

        self.assertEqual("scan_location", res.get("next_state"))

        self.assertEqual(
            self.location_reserve_1.id,
            res.get("data").get("scan_location").get("location").get("id"),
        )

        # Scan the proposed location
        res = self.service.dispatch("scan_location", params={"barcode": "RESERVE1"})

        self.assertEqual(
            "start_single",
            res.get("next_state"),
        )

        res = self.service.dispatch(
            "go_to_single", params={"location_id": self.location_reserve_1.id}
        )

        move_line_id = res.get("data").get("start_single").get("move_line").get("id")

        # Scan line
        res = self.service.dispatch(
            "scan_line",
            params={
                "barcode": self.product_a.barcode,
                "move_line_id": move_line_id,
                "location_id": self.location_reserve_1.id,
            },
        )

        # Validate the picking with a partial quantity
        res = self.service.dispatch(
            "set_destination_line",
            params={
                "barcode": "WH-STOCK",
                "confirmation": "",
                "location_id": self.location_reserve_1.id,
                "move_line_id": move_line_id,
                "quantity": 15,
            },
        )

        # The needed quantity to fullfill the demand was inferior
        # So, shopfloor asks to transfer the remaining quantity
        self.assertEqual("start_single", res.get("next_state"))
        self.assertDictEqual(
            {
                "message_type": "success",
                "body": "Content line transferred from Reserve 1 to Stock",
            },
            res.get("message"),
        )

        res = self.service.dispatch(
            "go_to_single", params={"location_id": self.location_reserve_1.id}
        )

        move_line_id = res.get("data").get("start_single").get("move_line").get("id")

        # Scan line
        res = self.service.dispatch(
            "scan_line",
            params={
                "barcode": self.product_a.barcode,
                "move_line_id": move_line_id,
                "location_id": self.location_reserve_1.id,
            },
        )

        moves = (
            self.env["stock.move"].search([("location_id", "=", self.reserve.id)])
            - refill_moves
        )
        self.assertEqual(
            1,
            len(moves),
        )
        self.assertEqual("assigned", moves.state)

        res = self.service.dispatch(
            "set_destination_line",
            params={
                "barcode": "WH-STOCK",
                "confirmation": "",
                "location_id": self.location_reserve_1.id,
                "move_line_id": move_line_id,
                "quantity": 5.0,
            },
        )

        # There is no refill quantities to do anymore
        self.assertEqual(
            "get_work",
            res.get("next_state"),
        )

    def test_scan_location_assignation_partial_superior(self):
        """
        Test case:

            We will try to do a superior quantity (but not the full!) than the needed quantities
            to refill the actual demand

            - Product A is present in several sub location of 'Stock':

                - Sub location 1: 10.0
                - Sub location 2: 10.0

            - Create a picking of 20.0 from Stock
            - Refill the Stock of Product A with 100.0
            - Launch the refill through Shopfloor

            - Refill 90.0 quantities (the destination location is maybe full)
            - No more work should be shown to shopfloor user
        """
        self.menu.sudo().full_location_reservation = True
        self.menu.sudo().allow_get_work = True

        # Refill one location
        self._update_qty_in_location(self.location_reserve_1, self.product_a, 100.0)

        # Search for Refill picking
        refill_moves = self.env["stock.move"].search(
            [("location_id", "=", self.reserve.id)]
        )

        # Check two lines have been created for one move
        self.assertEqual(1, len(refill_moves))
        self.assertEqual(2, len(refill_moves.move_line_ids))

        res = self.service.dispatch("find_work", params={})

        self.assertEqual("scan_location", res.get("next_state"))

        self.assertEqual(
            self.location_reserve_1.id,
            res.get("data").get("scan_location").get("location").get("id"),
        )

        # Scan the proposed location
        res = self.service.dispatch("scan_location", params={"barcode": "RESERVE1"})

        self.assertEqual(
            "start_single",
            res.get("next_state"),
        )

        res = self.service.dispatch(
            "go_to_single", params={"location_id": self.location_reserve_1.id}
        )

        move_line_id = res.get("data").get("start_single").get("move_line").get("id")

        # Scan line
        res = self.service.dispatch(
            "scan_line",
            params={
                "barcode": self.product_a.barcode,
                "move_line_id": move_line_id,
                "location_id": self.location_reserve_1.id,
            },
        )

        # Validate the picking with a partial quantity
        res = self.service.dispatch(
            "set_destination_line",
            params={
                "barcode": "WH-STOCK",
                "confirmation": "",
                "location_id": self.location_reserve_1.id,
                "move_line_id": move_line_id,
                "quantity": 90.0,
            },
        )

        # The needed quantity to fullfill the demand was inferior
        # So, shopfloor asks to transfer the remaining quantity
        self.assertEqual("get_work", res.get("next_state"))
        self.assertDictEqual(
            {
                "message_type": "success",
                "body": "Content line transferred from Reserve 1 to Stock",
            },
            res.get("message"),
        )

        # No further job to do
        res = self.service.dispatch("find_work", params={})
        self.assertEqual("get_work", res.get("next_state"))

        self.assertDictEqual(
            {"message_type": "warning", "body": "No available work could be found."},
            res.get("message"),
        )

    def test_scan_location_assignation_full(self):
        """
        Test case:

            We will try to do the full quantity
            to refill the actual demand

            - Product A is present in several sub location of 'Stock':

                - Sub location 1: 10.0
                - Sub location 2: 10.0

            - Create a picking of 20.0 from Stock
            - Refill the Stock of Product A with 100.0
            - Launch the refill through Shopfloor

            - Refill 100.0 quantities (the full quantity)
            - No more work should be shown to shopfloor user
        """
        self.menu.sudo().full_location_reservation = True
        self.menu.sudo().allow_get_work = True

        # Refill one location
        self._update_qty_in_location(self.location_reserve_1, self.product_a, 100.0)

        # Search for Refill picking
        refill_moves = self.env["stock.move"].search(
            [("location_id", "=", self.reserve.id)]
        )

        # Check two lines have been created for one move
        self.assertEqual(1, len(refill_moves))
        self.assertEqual(2, len(refill_moves.move_line_ids))

        res = self.service.dispatch("find_work", params={})

        self.assertEqual("scan_location", res.get("next_state"))

        self.assertEqual(
            self.location_reserve_1.id,
            res.get("data").get("scan_location").get("location").get("id"),
        )

        # Scan the proposed location
        res = self.service.dispatch("scan_location", params={"barcode": "RESERVE1"})

        self.assertEqual(
            "start_single",
            res.get("next_state"),
        )

        res = self.service.dispatch(
            "go_to_single", params={"location_id": self.location_reserve_1.id}
        )

        move_line_id = res.get("data").get("start_single").get("move_line").get("id")

        # Scan line
        res = self.service.dispatch(
            "scan_line",
            params={
                "barcode": self.product_a.barcode,
                "move_line_id": move_line_id,
                "location_id": self.location_reserve_1.id,
            },
        )

        # Validate the picking with a partial quantity
        res = self.service.dispatch(
            "set_destination_line",
            params={
                "barcode": "WH-STOCK",
                "confirmation": "",
                "location_id": self.location_reserve_1.id,
                "move_line_id": move_line_id,
                "quantity": 100.0,
            },
        )

        # The needed quantity to fullfill the demand was inferior
        # So, shopfloor asks to transfer the remaining quantity
        self.assertEqual("get_work", res.get("next_state"))
        self.assertDictEqual(
            {
                "message_type": "success",
                "body": "Content line transferred from Reserve 1 to Stock",
            },
            res.get("message"),
        )

        # No further job to do
        res = self.service.dispatch("find_work", params={})
        self.assertEqual("get_work", res.get("next_state"))

        self.assertDictEqual(
            {"message_type": "warning", "body": "No available work could be found."},
            res.get("message"),
        )

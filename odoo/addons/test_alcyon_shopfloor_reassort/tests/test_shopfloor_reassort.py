# Copyright 2023 Michael Tietz (MT Software) <mtietz@mt-software.de>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from .common import LocationContentTransferFullCommon


class LocationContentTransferFull(LocationContentTransferFullCommon):
    """Tests for Stock Content Transfer in Full Reservation context."""

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

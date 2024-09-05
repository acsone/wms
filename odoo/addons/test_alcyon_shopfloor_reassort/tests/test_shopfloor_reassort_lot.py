# Copyright 2023 Michael Tietz (MT Software) <mtietz@mt-software.de>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from .common import LocationContentTransferFullCommon


class LocationContentTransferFullLot(LocationContentTransferFullCommon):
    """Tests for Stock Content Transfer in Full Reservation context."""

    @classmethod
    def setUpClassBaseData(cls):
        res = super().setUpClassBaseData()
        user = cls.env.user
        cls.env = cls.env(user=1)
        cls.location_reserve_3 = cls.location_obj.create(
            {
                "name": "Reserve 3",
                "location_id": cls.location_src.id,
                "barcode": "RESERVE3",
            }
        )
        # Create a new product c with lot
        cls.product_c = cls.env["product.product"].create(
            {
                "name": "Product C with lots",
                "type": "product",
                "tracking": "lot",
                "barcode": "PRODUCTC",
            }
        )
        cls.lot_c_1 = cls.env["stock.lot"].create(
            {
                "name": "LOT 1",
                "product_id": cls.product_c.id,
            }
        )
        cls.lot_c_2 = cls.env["stock.lot"].create(
            {
                "name": "LOT 2",
                "product_id": cls.product_c.id,
            }
        )
        #
        cls._update_qty_in_location(
            cls.location_reserve_3, cls.product_c, 10, lot=cls.lot_c_1
        )
        cls._update_qty_in_location(
            cls.location_reserve_3, cls.product_c, 10, lot=cls.lot_c_2
        )

        cls.picking_lot = cls._create_picking(
            picking_type=cls.picking_type_out, lines=[(cls.product_c, 7)]
        )
        cls.picking_lot.action_assign()
        cls.env = cls.env(user=user.id)
        return res

    def test_scan_location_assignation_full_with_two_lots(self):
        """
        Test case:

            We will try to do the full quantity
            to refill the actual demand

            - Product A is present in same sub location of 'Stock':

                - Sub location 1: 10.0 (lot 1)
                - Sub location 1: 10.0 (lot 2)

            - Create a picking of 20.0 from Stock
            - Refill the Stock of Product A with 100.0
            - Launch the refill through Shopfloor

            - Refill 100.0 quantities (the full quantity)
            - No more work should be shown to shopfloor user
        """
        self.menu.sudo().full_location_reservation = True
        self.menu.sudo().allow_get_work = True

        # Refill one location
        self._update_qty_in_location(
            self.location_reserve_3, self.product_c, 100.0, lot=self.lot_c_1
        )

        # Search for Refill picking
        refill_moves = self.env["stock.move"].search(
            [
                ("location_id", "=", self.reserve.id),
                ("product_id", "=", self.product_c.id),
            ]
        )

        # Check two lines have been created for one move
        self.assertEqual(1, len(refill_moves))
        self.assertEqual(1, len(refill_moves.move_line_ids))

        self.service.dispatch("find_work", params={})

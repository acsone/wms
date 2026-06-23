# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from .common import CommonCase


class TestFullReservation(CommonCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._add_stock_to_product(cls.product_a, cls.location_src_a, 10)
        cls.picking_1 = cls._create_picking(lines=[(cls.product_a, 5)])
        cls.picking_1.move_line_ids.sudo().location_dest_id = cls.dispatch_location.id

    def test_no_full_reservation(self):
        """With full_location_reservation disabled, only the initially reserved qty is kept."""
        self.menu.sudo().full_location_reservation = False
        move_line = self._find_work()
        self.assertEqual(move_line.reserved_uom_qty, 5)
        self.assertEqual(move_line.location_id, self.location_src_a)

    def test_full_reservation(self):
        """With full_location_reservation enabled, all available qty at the location is
        reserved."""
        self.menu.sudo().full_location_reservation = True
        self._find_work()
        total_qty = sum(
            self.picking_1.move_line_ids.filtered(
                lambda l: l.product_id == self.product_a
                and l.location_id == self.location_src_a
            ).mapped("reserved_uom_qty")
        )
        self.assertEqual(total_qty, 10)


class TestFullReservationMultipleProducts(CommonCase):
    """Strict mode: full reservation must not spill over to other products."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.menu.sudo().full_location_reservation = True

        # Same location contains two different products.
        cls._add_stock_to_product(cls.product_a, cls.location_src_a, 10)
        cls._add_stock_to_product(cls.product_b, cls.location_src_a, 8)

        # Only part of the available qty is initially reserved for each product.
        cls.picking_1 = cls._create_picking(lines=[(cls.product_a, 5)])
        cls.picking_2 = cls._create_picking(lines=[(cls.product_b, 3)])

        (
            cls.picking_1 | cls.picking_2
        ).move_line_ids.sudo().location_dest_id = cls.dispatch_location.id

    def test_full_reservation_strict_does_not_overflow_to_other_product(self):
        """Full reservation with strict=True must only extend the reservation for
        the product of the assigned move line, leaving the other product untouched."""
        self._find_work()

        # product_a: full stock (10) must now be reserved.
        product_a_qty = sum(
            self.picking_1.move_line_ids.filtered(
                lambda l: l.product_id == self.product_a
                and l.location_id == self.location_src_a
            ).mapped("reserved_uom_qty")
        )
        self.assertEqual(
            product_a_qty,
            10,
            "Full reservation should have extended product_a to its full available qty",
        )

        # product_b: must remain at the originally reserved qty (3), not 8.
        product_b_qty = sum(
            self.picking_2.move_line_ids.filtered(
                lambda l: l.product_id == self.product_b
                and l.location_id == self.location_src_a
            ).mapped("reserved_uom_qty")
        )
        self.assertEqual(
            product_b_qty,
            3,
            "Strict mode must not extend the reservation to other products at the same "
            "location",
        )


class TestFullReservationMultipleLots(CommonCase):
    """Strict mode: full reservation must not spill over to other lots of the same product."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.menu.sudo().full_location_reservation = True
        cls._set_product_tracking_by_lot(cls.product_a)

        cls.lot_1 = cls._create_lot_for_product(cls.product_a, "LOT-001")
        cls.lot_2 = cls._create_lot_for_product(cls.product_a, "LOT-002")

        # Same location, same product, two different lots.
        cls._add_stock_to_product(cls.product_a, cls.location_src_a, 5, lot=cls.lot_1)
        cls._add_stock_to_product(cls.product_a, cls.location_src_a, 8, lot=cls.lot_2)

        # Only part of lot_1 is initially reserved; lot_2 has no picking.
        cls.picking_1 = cls._create_picking(lines=[(cls.product_a, 2)])
        cls.picking_1.move_line_ids.sudo().lot_id = cls.lot_1.id
        cls.picking_1.move_line_ids.sudo().location_dest_id = cls.dispatch_location.id

    def test_full_reservation_strict_does_not_overflow_to_other_lot(self):
        """Full reservation with strict=True must extend the reservation only for
        the lot of the assigned move line, leaving the other lot unreserved."""
        self._find_work()

        # lot_1: full stock at the location (5) must now be reserved.
        lot_1_qty = sum(
            self.picking_1.move_line_ids.filtered(
                lambda l: l.lot_id == self.lot_1
                and l.location_id == self.location_src_a
            ).mapped("reserved_uom_qty")
        )
        self.assertEqual(
            lot_1_qty,
            5,
            "Full reservation should have extended lot_1 to its full available qty",
        )

        # lot_2: must remain unreserved (no assigned move line for it).
        lot_2_lines = self.env["stock.move.line"].search(
            [
                ("lot_id", "=", self.lot_2.id),
                ("location_id", "=", self.location_src_a.id),
            ]
        )
        self.assertFalse(
            lot_2_lines,
            "Strict mode must not create a reservation for other lots at the same location",
        )

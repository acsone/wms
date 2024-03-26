# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .common import TestDeliverProcessBase


class TestSameProductMultiSoOnePrep(TestDeliverProcessBase):
    def test_00(self):
        """
        Scenario:

        The customer orders the same product twice, in different orders.
        One preparation is created for both orders for the same product.
        """
        sale = self._confirm_sale_order(
            products=[self.main_product], qty=2, partner=self.partner2
        )
        sal2 = self._confirm_sale_order(
            products=[self.main_product], qty=2, partner=self.partner2
        )
        out1 = self._get_picking_ship(sale)
        out2 = self._get_picking_ship(sal2)
        self.assertEqual(out1, out2)
        # open the channel, pick must be generated
        self.channel.action_unlock()
        pick = self._get_picking_pick(sale)
        pick2 = self._get_picking_pick(sal2)
        # pickings are equal
        self.assertEqual(pick, pick2)
        moves = pick.move_ids.filtered(lambda m: m.product_id == self.main_product)
        self.assertEqual(len(moves), 1)
        move_line = pick.move_line_ids.filtered(
            lambda ml: ml.product_id == self.main_product
        )

        self.assertEqual(len(move_line), 1)

        # check the additional products
        # first: into the ship we must have 2 lines for the main product
        # and 1 lines for the additional product
        ship = self._get_picking_ship(sale)
        main_moves = ship.move_ids.filtered(
            lambda m: m.product_id == self.main_product
            and m.state not in ("done", "cancel")
        )
        self.assertEqual(len(main_moves), 2)
        self.assertEqual(sum(main_moves.mapped("product_uom_qty")), 4)
        additional_moves = ship.move_ids.filtered(
            lambda m: m.product_id == self.additional_product
            and m.state not in ("done", "cancel")
        )
        self.assertEqual(len(additional_moves), 1)
        self.assertEqual(sum(additional_moves.mapped("product_uom_qty")), 20)

        # second: into the pick we must have 1 line for the main product
        # and 1 lines for the additional product
        additional_moves = pick.move_ids.filtered(
            lambda m: m.product_id == self.additional_product
            and m.state not in ("done", "cancel")
        )
        self.assertEqual(len(additional_moves), 1)
        self.assertEqual(sum(additional_moves.mapped("product_uom_qty")), 20)

        # if we've a new SO for the same product, we keep the same pick
        sal3 = self._confirm_sale_order(
            products=[self.main_product], qty=2, partner=self.partner2
        )
        ship3 = self._get_picking_ship(sal3)
        pick3 = self._get_picking_pick(sal3)
        self.assertEqual(ship, ship3)
        self.assertEqual(pick, pick3)
        for picking, nbr_main_move, nbr_addition_move in [(pick, 1, 1), (ship, 3, 1)]:
            main_moves = picking.move_ids.filtered(
                lambda m: m.product_id == self.main_product
                and m.state not in ("done", "cancel")
            )
            self.assertEqual(len(main_moves), nbr_main_move)
            self.assertEqual(sum(main_moves.mapped("product_uom_qty")), 6)
            additional_moves = picking.move_ids.filtered(
                lambda m: m.product_id == self.additional_product
                and m.state not in ("done", "cancel")
            )
            self.assertEqual(len(additional_moves), nbr_addition_move)
            self.assertEqual(sum(additional_moves.mapped("product_uom_qty")), 30)

    def test_auto_release_with_additional(self):
        """
        Scenario:

            We create and validate a first sale with an additional product and we
            unlock the channel.
            -> The picking is released. The additional product is added to the picking.
            We create and validate a second sale with the same product and we
            while the channel is in auto release mode.
            -> The new qty are added to the same picking.
        """
        sale = self._confirm_sale_order(
            products=[self.main_product], qty=2, partner=self.partner2
        )
        ship = self._get_picking_ship(sale)
        # open the channel, pick must be generated
        self.channel.action_unlock()
        pick = self._get_picking_pick(sale)

        # in both pick an ship we must have 1 line for the main product and 1 line for the additional product
        for picking in [pick, ship]:
            main_moves = picking.move_ids.filtered(
                lambda m: m.product_id == self.main_product
                and m.state not in ("done", "cancel")
            )
            self.assertEqual(len(main_moves), 1)
            self.assertEqual(sum(main_moves.mapped("product_uom_qty")), 2)
            additional_moves = picking.move_ids.filtered(
                lambda m: m.product_id == self.additional_product
                and m.state not in ("done", "cancel")
            )
            self.assertEqual(len(additional_moves), 1)
            self.assertEqual(sum(additional_moves.mapped("product_uom_qty")), 10)

        # create a new sale with the same product
        sale2 = self._confirm_sale_order(
            products=[self.main_product], qty=2, partner=self.partner2
        )
        ship2 = self._get_picking_ship(sale2)
        pick2 = self._get_picking_pick(sale2)

        # pick and ship must be grouped with the first sale
        self.assertEqual(ship, ship2)
        self.assertEqual(pick, pick2)

        for picking, nbr_main_move, nbr_addition_move in [(pick, 1, 1), (ship, 2, 1)]:
            main_moves = picking.move_ids.filtered(
                lambda m: m.product_id == self.main_product
                and m.state not in ("done", "cancel")
            )
            self.assertEqual(len(main_moves), nbr_main_move)
            self.assertEqual(sum(main_moves.mapped("product_uom_qty")), 4)
            additional_moves = picking.move_ids.filtered(
                lambda m: m.product_id == self.additional_product
                and m.state not in ("done", "cancel")
            )
            self.assertEqual(len(additional_moves), nbr_addition_move)
            self.assertEqual(sum(additional_moves.mapped("product_uom_qty")), 20)

    def test_simple_product(self):
        sale = self._confirm_sale_order(
            products=[self.product_2], qty=2, partner=self.partner2
        )
        ship = self._get_picking_ship(sale)
        # open the channel, pick must be generated
        self.channel.action_unlock()
        pick = self._get_picking_pick(sale)
        sale2 = self._confirm_sale_order(
            products=[self.product_2], qty=2, partner=self.partner2
        )
        ship2 = self._get_picking_ship(sale2)
        pick2 = self._get_picking_pick(sale2)

        # pick and ship must be grouped with the first sale
        self.assertEqual(ship, ship2)
        self.assertEqual(pick, pick2)

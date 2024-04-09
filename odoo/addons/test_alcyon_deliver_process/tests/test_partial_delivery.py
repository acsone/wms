# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import unittest

from .common import TestDeliverProcessBase


@unittest.skip("Test to be fixed after reworking the move merge mechanism")
class TestPartialDelivery(TestDeliverProcessBase):
    def test_00(self):
        """
        Scenario:

        The user prepares two orders and utilizes the same package for both.
        However, they later opt to deliver only one of the orders. In this case,
        the delivery should fail, and the user should be informed of the reason for
        the failure.
        This test load the planned shipment first
        The reservation cancel of the not done pick should allow the delivery
        """
        sale = self._confirm_sale_order(products=[self.main_product], qty=2)
        # open the channel, pick must be generated
        self.channel.action_unlock()
        pick = self._get_picking_pick(sale)
        ships = self._get_picking_ship(sale)
        self.channel.action_lock()
        # do the pick
        pick._put_in_pack(pick.move_line_ids)
        pick._action_done()
        ships = self._get_picking_ship(sale).filtered(lambda s: s.state == "assigned")
        ship1 = ships[0]
        ships._put_in_pack(ships.move_line_ids)
        ship1.release_channel_id = False
        # deliver the release channel
        self.channel.action_delivering()
        self.assertIn(
            "You cannot load this move line alone, you have to move the whole package content",
            self.channel.delivering_error,
        )
        self.assertEqual(self.channel.state, "delivering_error")
        #
        ship1.do_unreserve()
        #
        self.channel.action_delivering()
        self.assertFalse(self.channel.delivering_error)
        self.assertEqual(self.channel.state, "delivered")

    def test_01(self):
        """
        Scenario:

        The user prepares two orders and utilizes the same package for both.
        However, they later opt to deliver only one of the orders. In this case,
        the delivery should fail, and the user should be informed of the reason for
        the failure.
        This test load the planned shipment last
        The reservation cancel of the not done pick should allow the delivery
        """
        sale = self._confirm_sale_order(products=[self.main_product], qty=2)
        # open the channel, pick must be generated
        self.channel.action_unlock()
        pick = self._get_picking_pick(sale)
        self.channel.action_lock()
        # do the pick
        pick._put_in_pack(pick.move_line_ids)
        pick._action_done()
        ships = self._get_picking_ship(sale).filtered(lambda s: s.state == "assigned")
        ship2 = ships[1]
        ships._put_in_pack(ships.move_line_ids)
        ship2.release_channel_id = False
        # deliver the release channel
        self.channel.action_delivering()
        self.assertIn(
            "You cannot load this move line alone, you have to move the whole package content",
            self.channel.delivering_error,
        )
        self.assertEqual(self.channel.state, "delivering_error")
        #
        ship2.do_unreserve()
        #
        self.channel.action_delivering()
        self.assertFalse(self.channel.delivering_error)
        self.assertEqual(self.channel.state, "delivered")

    def test_02(self):
        """
        Scenario:

        The user prepares two orders and utilizes the same package for both.
        However, they choose to manually deliver one of the shipments. In this case,
        the automatic delivery shouldn't fail and the process should ignore done moves
        """
        sale = self._confirm_sale_order(products=[self.main_product], qty=2)
        # open the channel, pick must be generated
        self.channel.action_unlock()
        pick = self._get_picking_pick(sale)
        self.channel.action_lock()
        # do the pick
        pick._put_in_pack(pick.move_line_ids)
        pick._action_done()
        ships = self._get_picking_ship(sale).filtered(lambda s: s.state == "assigned")
        ship2 = ships[1]
        ships._put_in_pack(ships.move_line_ids)
        ship2._action_done()
        # deliver the release channel
        self.channel.action_delivering()
        self.assertFalse(self.channel.delivering_error)
        self.assertEqual(self.channel.state, "delivered")


class TestPartialDeliveryReport(TestDeliverProcessBase):
    def test_01(self):
        """
        Scenario:

        The use makes 2 orders and prepare one of them.
        It delivers the shipment and the call the method used to get the data for the delivery
        slip report. Since some moves are not done, they must be into the list of backorders
        """
        self.product_2.tracking = "none"
        self.product_3.tracking = "none"
        sale1 = self._confirm_sale_order(products=[self.product_2], qty=2)
        sale2 = self._confirm_sale_order(
            products=[self.product_2, self.product_3], qty=2
        )
        self.channel.action_unlock()
        ship1 = self._get_picking_ship(sale1)
        ship2 = self._get_picking_ship(sale2)
        # ships are the same
        self.assertEqual(ship1, ship2)
        pick1 = self._get_picking_pick(sale1)
        pick2 = self._get_picking_pick(sale2)
        # picks are the same
        self.assertEqual(pick1, pick2)
        self.channel.action_lock()
        # do the pick for product_2
        pick1.action_assign()
        move_line_product_2 = pick1.move_line_ids.filtered(
            lambda ml: ml.product_id == self.product_2
        )
        # moves for same product are grouped in pick
        move_line_product_2.qty_done = move_line_product_2.reserved_qty
        pick1._action_done()

        # do the ship for product_2
        ship1.action_assign()
        move_line_product_2 = ship1.move_line_ids.filtered(
            lambda ml: ml.product_id == self.product_2
        )
        # moves for same product are not grouped in ship
        for line in move_line_product_2:
            line.qty_done = line.reserved_qty

        # do the delivery
        ship1._action_done()

        moves_by_orders = ship1.get_moves_by_order()
        self.assertEqual(len(moves_by_orders), 2)
        sale1_moves = [
            moves_by_order[1]
            for moves_by_order in moves_by_orders
            if moves_by_order[0] == sale1
        ][0]
        move_lines = sale1_moves[0]
        # only product_2 is done
        self.assertEqual(len(move_lines), 1)
        self.assertEqual(move_lines[0].product_id, self.product_2)
        backorder_lines = sale1_moves[1]
        self.assertEqual(len(backorder_lines), 0)
        sale2_moves = [
            moves_by_order[1]
            for moves_by_order in moves_by_orders
            if moves_by_order[0] == sale2
        ][0]
        move_lines = sale2_moves[0]
        # only product_2 is done
        self.assertEqual(len(move_lines), 1)
        self.assertEqual(move_lines[0].product_id, self.product_2)
        self.assertEqual(len(move_lines), 1)
        # and we should have a backorder for product_3
        backorder_lines = sale2_moves[1]
        self.assertEqual(len(backorder_lines), 1)
        self.assertEqual(backorder_lines[0].product_id, self.product_3)

        # we create a new so for product_2 and we partially process product_3
        # since we process product_3 from sale2, the delivery slip report should show the backorder for product_3
        # if no qty is done for a SO in backorder, it should not appear in the report
        sale3 = self._confirm_sale_order(products=[self.product_2], qty=1)
        self.channel.action_sleep()
        self.channel.action_wake_up()
        pick3 = self._get_picking_pick(sale3)
        self.channel.action_lock()
        # do the pick for product_2
        pick3.action_assign()
        move_line_product_2 = pick3.move_line_ids.filtered(
            lambda ml: ml.product_id == self.product_2
        )
        # moves for same product are grouped in pick
        move_line_product_2.qty_done = move_line_product_2.reserved_qty
        # do the pick for product_3
        move_line_product_3 = pick3.move_line_ids.filtered(
            lambda ml: ml.product_id == self.product_3
        )
        move_line_product_3.qty_done = move_line_product_3.reserved_qty - 1
        pick3._action_done()

        # make the delivery
        ship3 = self._get_picking_ship(sale3)
        ship3.action_assign()
        for move_line in ship3.move_line_ids:
            move_line.qty_done = move_line.reserved_qty
        ship3._action_done()

        moves_by_orders = ship3.get_moves_by_order()
        self.assertEqual(len(moves_by_orders), 2)
        sale3_moves = [
            moves_by_order[1]
            for moves_by_order in moves_by_orders
            if moves_by_order[0] == sale3
        ][0]
        move_lines = sale3_moves[0]
        # only product_2 is done
        self.assertEqual(len(move_lines), 1)
        self.assertEqual(move_lines[0].product_id, self.product_2)
        backorder_lines = sale3_moves[1]
        self.assertEqual(len(backorder_lines), 0)
        sale2_moves = [
            moves_by_order[1]
            for moves_by_order in moves_by_orders
            if moves_by_order[0] == sale2
        ][0]
        move_lines = sale2_moves[0]
        # product_3 is partially done
        self.assertEqual(len(move_lines), 1)
        self.assertEqual(move_lines[0].product_id, self.product_3)
        backorder_lines = sale2_moves[1]
        self.assertEqual(len(backorder_lines), 1)
        self.assertEqual(backorder_lines[0].product_id, self.product_3)

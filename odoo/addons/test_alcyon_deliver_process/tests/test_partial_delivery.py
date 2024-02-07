# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from .common import TestDeliverProcessBase


class TestCancelAdditionalMove(TestDeliverProcessBase):
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

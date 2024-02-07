# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from .common import TestDeliverProcessBase


class TestCancelAdditionalMove(TestDeliverProcessBase):
    def test_00(self):
        """
        Deliver due to additional product cancel.

        how to reproduce:
        1- create so with additional product
        2- do the pick, no backorder for additional product
        3- deliver the release channel

        expect:
        the release channel delivered
        """
        # create the os, only ship is generated
        sale = self._confirm_sale_order(products=[self.main_product], qty=2)
        self._confirm_sale_order(products=[self.main_product], qty=2)
        ship = self._get_picking_ship(sale)
        pick = self._get_picking_pick(sale)
        self.assertEqual(len(ship), 1)
        self.assertEqual(len(pick), 0)
        self.assertEqual(ship.release_channel_id, self.channel)
        # open the channel, pick must be generated
        self.channel.action_unlock()
        pick = self._get_picking_pick(sale)
        ships = self._get_picking_ship(sale).filtered(lambda p: p.state == "waiting")
        self.assertEqual(ships.release_channel_id, self.channel)
        self.assertEqual(pick.release_channel_id, self.channel)
        self.assertEqual(pick.state, "assigned")
        self.channel.action_lock()
        # do the pick
        pick._put_in_pack(pick.move_line_ids)
        for move_line in pick.move_ids.move_line_ids:
            move_line.qty_done -= 1
        pick._action_done()
        self.assertTrue(pick.backorder_ids)
        #
        sale3 = self._confirm_sale_order(products=[self.main_product])
        ships = self._get_picking_ship(sale3)
        ships._put_in_pack(ships.move_line_ids)
        # deliver the release channel
        self.channel.action_delivering()
        self.assertFalse(self.channel.delivering_error)
        self.assertEqual(self.channel.state, "delivered")

    def test_01(self):
        sale = self._confirm_sale_order(products=[self.main_product], qty=2)
        self._confirm_sale_order(products=[self.main_product], qty=2)
        pick = self._get_picking_pick(sale)
        # open the channel, pick must be generated
        self.channel.action_unlock()
        pick = self._get_picking_pick(sale)
        pick.action_start()
        pick.action_assign()

# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from .common import TestDeliverProcessBase


class TestPartialDeliver(TestDeliverProcessBase):
    def test_00(self):
        """Test backorder unreleased after deliver an assigned to release channel at wakeup."""
        sale = self._confirm_sale_order(products=[self.main_product], qty=2)
        # open the channel, pick must be generated
        self.channel.action_unlock()
        pick = self._get_picking_pick(sale)
        ships = self._get_picking_ship(sale)
        self.channel.action_lock()
        # do the pick
        pick._put_in_pack(pick.move_line_ids)
        for move_line in pick.move_ids.move_line_ids:
            move_line.qty_done -= 1
        pick._action_done()
        self.assertTrue(pick.backorder_ids)
        ships = self._get_picking_ship(sale)
        # deliver the release channel
        self.channel.action_delivering()
        self.assertFalse(self.channel.delivering_error)
        self.assertEqual(self.channel.state, "delivered")
        backorder = ships.filtered(lambda s: s.state == "done").backorder_ids
        self.assertTrue(backorder)
        self.assertFalse(backorder.release_channel_id)
        self.assertTrue(backorder.need_release)
        self.channel.action_sleep()
        self.channel.action_wake_up()
        self.assertEqual(backorder.release_channel_id, self.channel)

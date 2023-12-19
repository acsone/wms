# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.queue_job.tests.common import trap_jobs

from .common import TestDeliverProcessBase


class TestPartialDeliver(TestDeliverProcessBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env["product.product"].create(
            {"name": "Test product", "tracking": "none", "type": "product"}
        )
        cls.env["stock.quant"]._update_available_quantity(cls.product, cls.loc_stock, 3)

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

    def test_01(self):
        """Test backorder unreleased after deliver an assigned to release channel at wakeup."""
        sale = self._confirm_sale_order(products=[self.product], qty=2)
        sale2 = self._confirm_sale_order(
            products=[self.product], qty=2, partner=self.partner2
        )
        # open the channel, pick must be generated
        with trap_jobs() as trap:
            self.channel.with_context(queue_job__no_delay=False).action_unlock()
            trap.perform_enqueued_jobs()
        pick = self._get_picking_pick(sale)
        pick2 = self._get_picking_pick(sale2)
        # do the pick
        pick._put_in_pack(pick.move_line_ids)
        for move_line in pick.move_ids.move_line_ids:
            move_line.qty_done = 2
        pick._action_done()
        self.assertEqual(pick2.state, "assigned")
        self.env["stock.quant"]._update_available_quantity(
            self.product, self.loc_stock, -1
        )
        pick2.printed = True
        pick2.move_ids._do_unreserve()
        self.assertEqual(pick2.state, "confirmed")
        # deliver the release channel
        self.channel.action_lock()
        self.channel.unrelease_picking()
        self.channel.action_delivering()
        self.assertFalse(self.channel.delivering_error)
        self.assertEqual(self.channel.state, "delivered")

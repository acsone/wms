# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError

from odoo.addons.queue_job.tests.common import trap_jobs

from .common import TestDeliverProcessBase


class TestUnreleaseAfterDeliver(TestDeliverProcessBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env["product.product"].create(
            {"name": "Test product", "tracking": "none", "type": "product"}
        )
        cls.env["stock.quant"]._update_available_quantity(cls.product, cls.loc_stock, 3)
        cls.lot = cls.env["stock.lot"].create(
            {"name": "lot", "product_id": cls.product.id}
        )

    def test_00(self):
        """Test backorder unreleased after deliver an assigned to release channel at wakeup."""
        sale = self._confirm_sale_order(products=[self.main_product], qty=2)
        # open the channel, pick must be generated
        self.channel.action_unlock()
        pick = self._get_picking_pick(sale)
        self._get_picking_ship(sale)
        self.channel.action_lock()
        # do the pick
        pick._put_in_pack(pick.move_line_ids)
        for move_line in pick.move_ids.move_line_ids:
            move_line.qty_done -= 1
        pick._action_done()
        self.assertTrue(pick.backorder_ids)
        self._get_picking_ship(sale)
        # deliver the release channel
        self.channel.action_delivering()
        self.assertFalse(self.channel.delivering_error)
        self.assertEqual(self.channel.state, "delivered")
        backorder = self._get_picking_ship(sale).filtered(
            lambda s: s.state not in ("done", "cancel")
        )
        self.assertTrue(backorder)
        self.assertFalse(backorder.release_channel_id)
        self.assertTrue(backorder.need_release)
        self.channel.action_sleep()
        self.channel.action_wake_up()
        self.assertEqual(backorder.release_channel_id, self.channel)

    def test_01(self):
        """
        Unrlease not allowed before delivering.

        When a picking is released and picked on the shopfloor, it is marked as printed.
        If the user discovers that the stock for a particular product is low, they
        declare a stock out, which unreserves the stock move, and the preparation pick
        becomes confirmed, not assigned.
        During delivery, the unrelease of this move is not allowed until the preparation
        loses the printed flag.
        """
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
        pick2.action_start()
        self.env["stock.quant"]._update_available_quantity(
            self.product, self.loc_stock, -1
        )
        pick2.move_ids._do_unreserve()
        pick2.move_ids._action_assign()
        self.assertEqual(pick2.state, "confirmed")
        # deliver the release channel
        self.channel.action_lock()
        self.channel.action_delivering()
        self.channel.unrelease_picking()
        self.channel.action_delivering()
        self.assertFalse(self.channel.delivering_error)
        self.assertEqual(self.channel.state, "delivered")

    def test_02(self):
        """
        Unrlease not allowed before delivering.

        When a picking is released and picked on the shopfloor, it is marked as printed.
        During delivery, the unrelease of this move is not allowed until the preparation
        loses the printed flag.
        """
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
        pick2.action_start()
        # deliver the release channel
        self.channel.action_lock()
        with self.assertRaises(
            UserError, msg="One of the pickings to deliver for channel is started"
        ):
            self.channel.action_delivering()
        pick2.action_cancel_start()
        self.channel.unrelease_picking()
        self.channel.action_delivering()
        self.assertFalse(self.channel.delivering_error)
        self.assertEqual(self.channel.state, "delivered")

    def test_03(self):
        """
        Unrlease not allowed before delivering.

        When a picking is released and picked on the shopfloor, it is marked as printed.
        During delivery, the unrelease of this move is not allowed until the preparation
        partially available loses the printed flag.
        """
        self.env["stock.quant"]._update_available_quantity(
            self.product, self.loc_stock, -1
        )
        self.env["stock.quant"]._update_available_quantity(
            self.product, self.loc_stock, 2, lot_id=self.lot
        )
        sale = self._confirm_sale_order(products=[self.product], qty=2)
        sale2 = self._confirm_sale_order(
            products=[self.product], qty=2, partner=self.partner2
        )
        # open the channel, pick must be generated
        with trap_jobs() as trap:
            self.channel.with_context(queue_job__no_delay=False).action_unlock()
            trap.perform_enqueued_jobs()
        picks = self._get_picking_pick(sale) | self._get_picking_pick(sale2)
        pick_with_lot = picks.filtered("move_line_ids.lot_id")
        pick_without_lot = picks - pick_with_lot

        pick_with_lot.move_type = "one"
        # do the pick_without_lot
        pick_without_lot._put_in_pack(pick_without_lot.move_line_ids)
        for move_line in pick_without_lot.move_ids.move_line_ids:
            move_line.qty_done = 2
        pick_without_lot._action_done()
        self.assertEqual(pick_with_lot.state, "assigned")
        self.assertEqual(pick_with_lot.move_line_ids.lot_id, self.lot)
        pick_with_lot.action_start()
        self.env["stock.quant"]._update_available_quantity(
            self.product, self.loc_stock, -1, lot_id=self.lot
        )

        pick_with_lot.do_unreserve()
        pick_with_lot.action_assign()
        self.assertEqual(pick_with_lot.move_ids.state, "partially_available")
        # deliver the release channel
        self.channel.action_lock()
        self.channel.action_delivering()
        self.channel.unrelease_picking()
        self.channel.action_delivering()
        self.assertFalse(self.channel.delivering_error)
        self.assertEqual(self.channel.state, "delivered")

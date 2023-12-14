# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import Command

from odoo.addons.alc_additional_product_stock.tests.common import StockPickingTestCase


class TestCancelAdditionalMove(StockPickingTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, queue_job__no_delay=True))
        cls.env["stock.release.channel"].search([]).unlink()
        cls.dock = cls.env.ref("shipment_advice.stock_dock_demo")
        cls.channel = cls.env["stock.release.channel"].create(
            {
                "name": "Release Channel",
                "release_mode": "auto",
                "state": "locked",
                "shipment_planning_method": "simple",
                "partner_ids": [Command.set(cls.partner1.ids)],
                "warehouse_id": cls.warehouse_1.id,
                "dock_id": cls.dock.id,
            }
        )
        cls.warehouse_1.route_ids.available_to_promise_defer_pull = True
        cls.warehouse_1.out_type_id.propagate_to_pickings_chain = True
        cls.warehouse_1.out_type_id.no_backorder_for_additional_product = True
        cls.warehouse_1.out_type_id.group_pickings_by_customer = True
        cls.warehouse_1.out_type_id.group_pickings = True
        cls.warehouse_1.pick_type_id.no_backorder_for_additional_product = True
        cls.env.user.groups_id += cls.env.ref(
            "alc_stock_picking_cancel_permission.group_picking_cancel"
        )

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
        self.channel.action_sleep()
        self.channel.action_wake_up()
        sale4 = self._confirm_sale_order(products=[self.main_product], qty=1000)
        picks = self._get_picking_pick(sale4).filtered(lambda p: p.state == "assigned")
        self.channel.action_lock()
        picks._put_in_pack(picks.move_line_ids)
        picks._action_done()
        ships = self._get_picking_ship(sale4)
        ships._put_in_pack(ships.move_line_ids)
        self.channel.action_delivering()
        self.assertFalse(self.channel.delivering_error)

    def test_01(self):
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

    def test_02(self):
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

    def test_03(self):
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

    def test_04(self):
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

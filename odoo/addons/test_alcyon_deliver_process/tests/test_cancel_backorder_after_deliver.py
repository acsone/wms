# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.queue_job.tests.common import trap_jobs

from .common import TestDeliverProcessBase


class TestCancelBackorder(TestDeliverProcessBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env["product.product"].create(
            {"name": "Test product", "tracking": "none", "type": "product"}
        )
        cls.env["stock.quant"]._update_available_quantity(cls.product, cls.loc_stock, 3)

    def test_00(self):
        """Partner choice cancel."""
        self.partner1.sale_reason_backorder_strategy = "cancel"

        # The expected behavior on Delivery picking type
        self.warehouse_1.out_type_id.write(
            {"backorder_reason_transparent_cancel": True, "backorder_reason_sale": True}
        )
        sale = self._confirm_sale_order(products=[self.product], qty=2)
        # open the channel, pick must be generated
        with trap_jobs() as trap:
            self.channel.with_context(queue_job__no_delay=False).action_unlock()
            trap.perform_enqueued_jobs()
        pick = self._get_picking_pick(sale)
        self._get_picking_ship(sale)
        self.channel.action_lock()
        # do the pick
        pick._put_in_pack(pick.move_line_ids)
        for move_line in pick.move_ids.move_line_ids:
            move_line.qty_done -= 1
        pick._action_done()
        self.assertTrue(pick.backorder_ids)
        ship = self._get_picking_ship(sale).filtered(lambda p: p.state == "assigned")
        # deliver the release channel
        # This should launch the confirmation choice wizard as we should pick the backorder to ensure
        # customer delivery
        # We cancel the bakcorder manually
        res = self.channel.action_deliver()
        self.assertEqual(
            "stock.release.channel.deliver.check.wizard", res.get("res_model", False)
        )
        self.assertFalse(self.channel.delivering_error)
        self.assertEqual(self.channel.state, "locked")

        pick.backorder_ids.with_user(self.stock_admin).action_cancel()
        self.channel.action_deliver()

        self.assertEqual(ship.state, "done")
        self.assertFalse(ship.backorder_ids)

    def test_01(self):
        """Partner choice create."""
        self.partner1.sale_reason_backorder_strategy = "create"
        sale = self._confirm_sale_order(products=[self.product], qty=2)
        # open the channel, pick must be generated
        with trap_jobs() as trap:
            self.channel.with_context(queue_job__no_delay=False).action_unlock()
            trap.perform_enqueued_jobs()
        pick = self._get_picking_pick(sale)
        self._get_picking_ship(sale)
        self.channel.action_lock()
        # do the pick
        pick._put_in_pack(pick.move_line_ids)
        for move_line in pick.move_ids.move_line_ids:
            move_line.qty_done -= 1
        pick._action_done()
        self.assertTrue(pick.backorder_ids)
        ship = self._get_picking_ship(sale).filtered(lambda p: p.state == "assigned")

        res = self.channel.action_deliver()
        self.assertEqual(
            "stock.release.channel.deliver.check.wizard", res.get("res_model", False)
        )
        self.assertFalse(self.channel.delivering_error)
        self.assertEqual(self.channel.state, "locked")

        # deliver the release channel
        pick.backorder_ids.with_user(self.stock_admin).action_cancel()
        self.channel.action_deliver()
        self.assertFalse(self.channel.delivering_error)
        self.assertEqual(self.channel.state, "delivered")
        self.assertEqual(ship.state, "done")
        self.assertTrue(ship.backorder_ids)

    def test_02(self):
        """Partner choice cancel.

        test normal delivery we continue to get backorder wizard
        """
        self.partner1.sale_reason_backorder_strategy = "cancel"
        sale = self._confirm_sale_order(products=[self.product], qty=2)
        # open the channel, pick must be generated
        with trap_jobs() as trap:
            self.channel.with_context(queue_job__no_delay=False).action_unlock()
            trap.perform_enqueued_jobs()
        pick = self._get_picking_pick(sale)
        self._get_picking_ship(sale)
        self.channel.action_lock()
        # do the pick
        pick._put_in_pack(pick.move_line_ids)
        for move_line in pick.move_ids.move_line_ids:
            move_line.qty_done -= 1
        pick._action_done()
        self.assertTrue(pick.backorder_ids)
        ship = self._get_picking_ship(sale).filtered(lambda p: p.state == "assigned")
        # deliver the release channel
        ship.action_set_quantities_to_reservation()
        action = ship.button_validate()
        self.assertEqual(ship.state, "assigned")
        self.assertEqual(action.get("res_model"), "stock.backorder.confirmation")

    def test_03(self):
        """Partner choice cancel.

        test normal delivery we continue to get backorder
        """
        self.partner1.sale_reason_backorder_strategy = "cancel"
        sale = self._confirm_sale_order(products=[self.product], qty=2)
        # open the channel, pick must be generated
        with trap_jobs() as trap:
            self.channel.with_context(queue_job__no_delay=False).action_unlock()
            trap.perform_enqueued_jobs()
        pick = self._get_picking_pick(sale)
        self._get_picking_ship(sale)
        self.channel.action_lock()
        # do the pick
        pick._put_in_pack(pick.move_line_ids)
        for move_line in pick.move_ids.move_line_ids:
            move_line.qty_done -= 1
        pick._action_done()
        self.assertTrue(pick.backorder_ids)
        ship = self._get_picking_ship(sale).filtered(lambda p: p.state == "assigned")
        # deliver the release channel
        ship.action_set_quantities_to_reservation()
        ship._action_done()
        self.assertEqual(ship.state, "done")
        self.assertTrue(ship.backorder_ids)

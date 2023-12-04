# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import Command

from odoo.addons.alc_additional_product_stock.tests.common import StockPickingTestCase


class TestCancelAdditionalMove(StockPickingTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, queue_job__no_delay=True))
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
        cls.warehouse_1.route_ids[1].available_to_promise_defer_pull = True
        cls.warehouse_1.out_type_id.propagate_to_pickings_chain = True
        cls.warehouse_1.out_type_id.no_backorder_for_additional_product = True

    def test_00(self):
        """
        Fail to deliver due to additional product cancel.

        how to reproduce:
        1- create so with additional product
        2- do the pick and a create a backorder
        3- deliver the release channel
        """
        # create the os, only ship is generated
        sale = self._confirm_sale_order(products=[self.main_product])
        ship = self._get_picking_ship(sale)
        pick = self._get_picking_pick(sale)
        self.assertEqual(len(ship), 1)
        self.assertEqual(len(pick), 0)
        self.assertEqual(ship.release_channel_id, self.channel)
        # open the channel, pick must be generated
        self.channel.action_unlock()
        pick = self._get_picking_pick(sale)
        ships = self._get_picking_ship(sale).filtered(lambda p: p.state == "waiting")
        self.assertEqual(len(pick), 1)
        self.assertEqual(ships.release_channel_id, self.channel)
        self.assertEqual(pick.release_channel_id, self.channel)
        self.assertEqual(pick.state, "assigned")
        # do the pick
        pick.action_start()
        pick.action_set_quantities_to_reservation()
        pick.move_ids.filtered("is_additional_move").move_line_ids.qty_done -= 1
        pick._action_done()
        self.assertTrue(pick.backorder_ids)
        # deliver the release channel
        self.channel.action_lock()
        self.channel.action_delivering()
        # FIXME: the additional line should be canceled
        self.assertEqual(self.channel.state, "delivering_error")
        expected_error = (
            "This action is not allowed because it leads to the "
            "cancellation of a move of a started picking."
        )
        self.assertIn(expected_error, self.channel.delivering_error)

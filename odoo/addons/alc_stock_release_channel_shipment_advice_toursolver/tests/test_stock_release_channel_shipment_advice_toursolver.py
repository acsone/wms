# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo.addons.stock_release_channel.tests.common import ChannelReleaseCase


def _do_picking(picking):
    for move in picking.move_ids:
        move.quantity_done = move.product_qty
    picking._action_done()


class TestStockReleaseChannelShipmentAdviceToursolver(ChannelReleaseCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.channel.process_end_time = 14
        cls.channel.shipment_advice_departure_time = 12
        cls.channel.auto_allow_pick_time_before_leave = 0.5
        cls.backend = cls.env.ref(
            "shipment_advice_planner_toursolver.toursolver_backend_default"
        )
        cls.backend.loading_duration = 180

    def test_00(self):
        """Test planned_start_loading_time."""
        self.assertEqual(self.channel.planned_start_loading_time, 9)
        self.channel.shipment_advice_departure_time = 14
        self.assertEqual(self.channel.planned_start_loading_time, 11)
        self.channel.loading_duration = 120
        self.channel.shipment_advice_departure_time = 16
        self.assertEqual(self.channel.planned_start_loading_time, 14)

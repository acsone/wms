# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import datetime

from freezegun import freeze_time

from odoo.addons.stock_release_channel.tests.common import ChannelReleaseCase


def _do_picking(picking):
    for move in picking.move_ids:
        move.quantity_done = move.product_qty
    picking._action_done()


class TestStockReleaseChannelShipmentAdviceToursolver(ChannelReleaseCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.channel.leave_planned_time = 12
        cls.channel.auto_allow_pick_time_before_leave = 0.5
        cls.backend = cls.env.ref(
            "shipment_advice_planner_toursolver.toursolver_backend_default"
        )
        cls.backend.loading_duration = 180

    def test_00(self):
        """Test planned_start_loading_time."""
        self.assertEqual(self.channel.planned_start_loading_time, 9)
        self.channel.leave_planned_time = 14
        self.assertEqual(self.channel.planned_start_loading_time, 11)
        self.backend.loading_duration = 120
        self.channel.leave_planned_time = 16
        self.assertEqual(self.channel.planned_start_loading_time, 14)

    @freeze_time("2023-04-01 12:00:00")
    def test_01(self):
        """Test leave_planned_datetime."""
        self.assertEqual(self.channel.leave_planned_datetime, datetime(2023, 4, 2, 10))
        self.channel.leave_planned_time = 16
        self.assertEqual(self.channel.leave_planned_datetime, datetime(2023, 4, 1, 14))
        self.channel.leave_planned_time = 9.5
        self.assertEqual(
            self.channel.leave_planned_datetime, datetime(2023, 4, 2, 7, 30)
        )
        self.env.user.tz = "UTC"
        self.channel.leave_planned_time = 18
        self.assertEqual(
            self.channel.leave_planned_datetime, datetime(2023, 4, 1, 18, 0)
        )

# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from contextlib import contextmanager
from datetime import datetime

from freezegun import freeze_time

from odoo.addons.queue_job.tests.common import trap_jobs
from odoo.addons.stock_release_channel.tests.common import ChannelReleaseCase


def _do_picking(picking):
    for move in picking.move_ids:
        move.quantity_done = move.product_qty
    picking._action_done()


class TestStockReleaseChannelPickAllowed(ChannelReleaseCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.pickings = cls.picking | cls.picking2
        output_loc = cls.pickings.move_ids.location_id
        cls._update_qty_in_location(output_loc, cls.product1, 100)
        cls._update_qty_in_location(output_loc, cls.product2, 100)
        cls.pickings.move_ids.write({"procure_method": "make_to_stock"})
        cls.pickings.action_assign()
        cls.channel.picking_ids = cls.pickings
        cls.channel.pick_allowed = True
        cls.channel.auto_disallow_pick = True
        cls.channel.auto_allow_pick = True
        cls.channel.process_end_time = 14
        cls.channel.shipment_advice_departure_time = 12
        cls.channel.auto_allow_pick_time_before_leave = 0.5
        cls.channel.state = "asleep"
        cls.channel.process_end_time = 14
        cls.backend = cls.env.ref(
            "shipment_advice_planner_toursolver.toursolver_backend_default"
        )
        cls.channel.loading_duration = 180

    @contextmanager
    def _audit_new_logs(self):
        Logs = self.env["stock.release.channel.pick.allowed.log"]
        logs = Logs.search([("release_channel_id", "=", self.channel.id)])
        yield
        new_logs = Logs.search([("release_channel_id", "=", self.channel.id)]) - logs
        self.new_logs = new_logs

    def test_00(self):
        """
        The picking type of the started picking is not set to be managed individually.

        -> test that the channel disallow pick after all picking started
        """
        self.assertTrue(self.channel.pick_allowed)
        self.picking.action_start()
        self.assertTrue(self.channel.pick_allowed)
        self.picking2.action_start()
        self.assertFalse(self.channel.pick_allowed)

    def test_01(self):
        """
        The picking type of the started picking is set to be managed individually.

        -> test that the channel disallow pick for the give type after picking started
        and the channel continue to allow piking
        """
        picking_type = self.picking.picking_type_id
        picking_type.release_channel_can_allow_pick = True
        self.assertTrue(self.channel.pick_allowed)
        self.assertTrue(self.channel._get_picking_type_pick_allowed(picking_type.id))
        self.pickings.action_start()
        self.assertTrue(self.channel.pick_allowed)
        self.assertFalse(self.channel._get_picking_type_pick_allowed(picking_type.id))

    def test_02(self):
        """
        The channel is not set to disallow pick automatically.

        -> test no effect after picking started
        """
        self.channel.auto_disallow_pick = False
        self.assertTrue(self.channel.pick_allowed)
        self.picking.action_start()
        self.assertTrue(self.channel.pick_allowed)

    @freeze_time("2023-04-01 12:00:00")
    def test_03(self):
        """Test that a job is planned to allow pick at action_wake_up."""
        self.channel.pick_allowed = False
        self.assertFalse(self.channel.pick_allowed)
        with trap_jobs() as trap:
            self.channel.action_wake_up()
            trap.assert_enqueued_job(
                self.channel._set_pick_allowed,
                kwargs={"pick_allowed": True, "picking_type": None},
                properties={"eta": datetime(2023, 4, 2, 6, 30)},
            )
            self.assertFalse(self.channel.pick_allowed)
            trap.perform_enqueued_jobs()
            self.assertTrue(self.channel.pick_allowed)

    def test_04(self):
        """
        The channel is not set to allow pick automatically.

        -> test no effect after all pickings are done
        """
        self.channel.auto_allow_pick = False
        self.channel.pick_allowed = False
        self.assertFalse(self.channel.pick_allowed)
        _do_picking(self.picking)
        self.assertEqual(self.picking.state, "done")
        _do_picking(self.picking2)
        self.assertEqual(self.picking2.state, "done")
        self.assertFalse(self.channel.pick_allowed)

    @freeze_time("2023-04-01 12:00:00")
    def test_05(self):
        """Test auto_allow_pick_datetime."""
        self.assertEqual(
            self.channel.auto_allow_pick_datetime, datetime(2023, 4, 2, 6, 30)
        )
        self.channel.auto_allow_pick_time_before_leave = 1.5
        self.assertEqual(
            self.channel.auto_allow_pick_datetime, datetime(2023, 4, 2, 5, 30)
        )
        self.channel.shipment_advice_departure_time = 14
        self.channel.auto_allow_pick_time_before_leave = 0
        self.assertEqual(
            self.channel.auto_allow_pick_datetime, datetime(2023, 4, 2, 9, 0)
        )
        self.channel.loading_duration = 120
        self.channel.shipment_advice_departure_time = 16
        self.assertEqual(
            self.channel.auto_allow_pick_datetime, datetime(2023, 4, 2, 12, 0)
        )
        self.env.user.tz = "UTC"
        self.channel.shipment_advice_departure_time = 18
        self.assertEqual(
            self.channel.auto_allow_pick_datetime, datetime(2023, 4, 1, 16, 0)
        )

    @freeze_time("2023-04-01 12:00:00")
    def test_06(self):
        """
        Auto_allow_pick_time_before_leave changes so the set_pick_allowed job must be.

        rescheduled
        """
        self.channel.pick_allowed = False
        self.assertFalse(self.channel.pick_allowed)
        self.channel.action_wake_up()
        job = self.env["queue.job"].search(
            [
                ("model_name", "=", self.channel._name),
                ("method_name", "=", "_set_pick_allowed"),
            ]
        )
        self.assertEqual(job.eta, datetime(2023, 4, 2, 6, 30))
        with trap_jobs() as trap:
            self.channel.auto_allow_pick_time_before_leave = 1.5
            self.assertEqual(job.state, "done")
            self.assertEqual(
                job.result,
                "Change on hours for release channel pick allowed."
                "This job is set to done, a new one is created.",
            )
            trap.assert_enqueued_job(
                self.channel._set_pick_allowed,
                kwargs={"pick_allowed": True, "picking_type": None},
                properties={"eta": datetime(2023, 4, 2, 5, 30)},
            )
            self.assertEqual(self.channel.auto_allow_pick_time_before_leave, 1.5)

    @freeze_time("2023-04-01 12:00:00")
    def test_07(self):
        """
        Leave_planned_time changes so the set_pick_allowed job must be.

        rescheduled
        """
        self.channel.pick_allowed = False
        self.assertFalse(self.channel.pick_allowed)
        self.channel.action_wake_up()
        job = self.env["queue.job"].search(
            [
                ("model_name", "=", self.channel._name),
                ("method_name", "=", "_set_pick_allowed"),
            ]
        )
        self.assertEqual(job.eta, datetime(2023, 4, 2, 6, 30))
        with trap_jobs() as trap:
            self.channel.shipment_advice_departure_time = 14
            self.assertEqual(job.state, "done")
            self.assertEqual(
                job.result,
                "Change on hours for release channel pick allowed."
                "This job is set to done, a new one is created.",
            )
            trap.assert_enqueued_job(
                self.channel._set_pick_allowed,
                kwargs={"pick_allowed": True, "picking_type": None},
                properties={"eta": datetime(2023, 4, 2, 8, 30)},
            )
            self.assertEqual(self.channel.shipment_advice_departure_time, 14)

    def test_08(self):
        """Action_sleep disallow pick automatically."""
        self.channel.pick_allowed = True
        self.channel.state = "open"
        self.assertTrue(self.channel.pick_allowed)
        self.channel.action_sleep()
        self.assertFalse(self.channel.pick_allowed)

    def test_09(self):
        """
        Test channel pick_allowed depending on pickings pick_allowed.

        - if all pickings disabled -> channel disabled
        - if one picking enabled -> channel enable
        - channel enable -> enable all pickings
        - channel disable -> disable all pickings
        """
        _states = self.channel._get_all_picking_type_ids_state
        picking_types = self.env["stock.picking.type"].search([], limit=2)
        pt1_id = picking_types[0].id
        pt2_id = picking_types[1].id
        picking_types.release_channel_can_allow_pick = True
        self.assertTrue(self.channel.pick_allowed)
        self.assertDictEqual(_states(), {pt1_id: True, pt2_id: True})
        self.channel._toggle_pick_allowed_channel()
        self.assertFalse(self.channel.pick_allowed)
        self.assertDictEqual(_states(), {pt1_id: False, pt2_id: False})
        self.channel._toggle_pick_allowed_for_picking_type_id(pt1_id)
        self.assertTrue(self.channel.pick_allowed)
        self.assertDictEqual(_states(), {pt1_id: True, pt2_id: False})
        self.channel._toggle_pick_allowed_for_picking_type_id(pt1_id)
        self.assertFalse(self.channel.pick_allowed)
        self.assertDictEqual(_states(), {pt1_id: False, pt2_id: False})
        self.channel._toggle_pick_allowed_channel()
        self.assertDictEqual(_states(), {pt1_id: True, pt2_id: True})

    def test_10(self):
        """
        Test action sleep and wakeup impact on pick_allowed.

        if auto_allow_pick is set, pick_allowed is enabled for channel and pick types
        if auto_disallow_pick is set, pick_allowed is disabled for channel and pick types
        """
        _states = self.channel._get_all_picking_type_ids_state
        picking_types = self.env["stock.picking.type"].search([], limit=2)
        pt1_id = picking_types[0].id
        pt2_id = picking_types[1].id
        picking_types.release_channel_can_allow_pick = True
        channel = self.channel.with_context(queue_job__no_delay=True)
        channel.write({"auto_allow_pick": True, "auto_disallow_pick": True})
        channel._toggle_pick_allowed_channel()
        self.assertFalse(channel.pick_allowed)
        self.assertDictEqual(_states(), {pt1_id: False, pt2_id: False})
        channel.action_wake_up()
        self.assertTrue(channel.pick_allowed)
        self.assertDictEqual(_states(), {pt1_id: True, pt2_id: True})
        channel.action_sleep()
        self.assertFalse(channel.pick_allowed)
        self.assertDictEqual(_states(), {pt1_id: False, pt2_id: False})

    def test_11(self):
        """
        Test action sleep and wakeup impact on pick_allowed.

        if auto_allow_pick is not set, no change at pick_allowed
        if auto_disallow_pick is set, no change at pick_allowed
        """
        _states = self.channel._get_all_picking_type_ids_state
        picking_types = self.env["stock.picking.type"].search([], limit=2)
        pt1_id = picking_types[0].id
        pt2_id = picking_types[1].id
        picking_types.release_channel_can_allow_pick = True
        channel = self.channel.with_context(queue_job__no_delay=True)
        channel.write({"auto_allow_pick": False, "auto_disallow_pick": False})
        channel._toggle_pick_allowed_channel()
        self.assertFalse(channel.pick_allowed)
        self.assertDictEqual(_states(), {pt1_id: False, pt2_id: False})
        channel.action_wake_up()
        self.assertFalse(channel.pick_allowed)
        self.assertDictEqual(_states(), {pt1_id: False, pt2_id: False})
        channel._toggle_pick_allowed_channel()
        self.assertTrue(channel.pick_allowed)
        self.assertDictEqual(_states(), {pt1_id: True, pt2_id: True})
        channel.action_sleep()
        self.assertTrue(channel.pick_allowed)
        self.assertDictEqual(_states(), {pt1_id: True, pt2_id: True})

    def test_12(self):
        """Test log message when pick_allowed is changed."""

        picking_types = self.env["stock.picking.type"].search([], limit=2)
        pt1_id = picking_types[0].id
        pt2_id = picking_types[1].id
        picking_types.release_channel_can_allow_pick = True
        channel = self.channel.with_context(queue_job__no_delay=True)
        _states = self.channel._get_all_picking_type_ids_state
        channel.write({"auto_allow_pick": False, "auto_disallow_pick": False})
        with self._audit_new_logs():
            channel._toggle_pick_allowed_channel()
        self.assertEqual(len(self.new_logs), 2)
        self.assertEqual(self.new_logs.mapped("picking_type_id"), picking_types[:2])
        self.assertEqual(
            self.new_logs.mapped("allowed"),
            [channel.pick_allowed, channel.pick_allowed],
        )
        old_allowed = channel.pick_allowed
        with self._audit_new_logs():
            channel._toggle_pick_allowed_channel()
        self.assertEqual(len(self.new_logs), 2)
        self.assertEqual(
            self.new_logs.mapped("allowed"), [not old_allowed, not old_allowed]
        )
        # change only one picking type
        with self._audit_new_logs():
            channel._toggle_pick_allowed_for_picking_type_id(pt1_id)
        self.assertEqual(len(self.new_logs), 1)
        self.assertEqual(self.new_logs.picking_type_id, picking_types[0])
        self.assertEqual(self.new_logs.allowed, old_allowed)
        # check we log the right user
        with self.with_user("demo"), self._audit_new_logs():
            self.env[channel._name].browse(channel.id).with_context(
                queue_job__no_delay=True
            )._toggle_pick_allowed_for_picking_type_id(pt2_id)
        self.assertEqual(len(self.new_logs), 1)
        self.assertEqual(self.new_logs.picking_type_id, picking_types[1])
        self.assertEqual(self.new_logs.allowed, old_allowed)
        self.assertEqual(self.new_logs.create_uid, self.env.ref("base.user_demo"))

        # delete all logs
        Logs = self.env["stock.release.channel.pick.allowed.log"]
        Logs.cron_garbage_collector(nb_days=0)
        existing = Logs.search_count([])
        self.assertEqual(existing, 0)

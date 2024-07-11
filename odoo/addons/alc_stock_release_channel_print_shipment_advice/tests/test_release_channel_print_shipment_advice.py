# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError
from odoo.tools import mute_logger

from odoo.addons.queue_job.tests.common import trap_jobs
from odoo.addons.stock_release_channel.tests.common import ChannelReleaseCase


class TestStockReleaseChannelDeliver(ChannelReleaseCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env.user.company_id.shipment_advice_run_in_queue_job = True
        output_loc = cls.channel.picking_ids.move_ids.location_id
        cls._update_qty_in_location(output_loc, cls.product1, 100)
        cls._update_qty_in_location(output_loc, cls.product2, 100)
        cls.channel.picking_ids.move_ids.write({"procure_method": "make_to_stock"})
        cls.channel.picking_ids.action_assign()
        cls.dock = cls.env.ref("shipment_advice.stock_dock_demo")
        cls.dock.warehouse_id = cls.wh
        cls.warehouse2 = cls.env.ref("stock.stock_warehouse_shop0")
        cls.channel.dock_id = cls.dock
        cls.channel.action_lock()
        cls.channel.shipment_planning_method = "simple"
        cls.pickings = cls.channel.picking_to_plan_ids

    def test_00(self):
        """Shipment advices are created and automatically processed."""
        with trap_jobs() as trap_rc:
            self.channel.action_deliver()
            self.assertEqual(self.channel.state, "delivering")
            trap_rc.assert_enqueued_job(self.channel._action_deliver)
            with trap_jobs() as trap_sa:
                trap_rc.perform_enqueued_jobs()
                advices = self.channel.shipment_advice_ids.filtered(
                    lambda s: s.state not in ("cancel", "done")
                )
                trap_sa.assert_enqueued_job(advices._auto_process)
                with trap_jobs() as trap_sap:
                    trap_sa.perform_enqueued_jobs()
                    trap_sap.perform_enqueued_jobs()
                shipment_advice = advices.filtered(lambda s: s.state == "done")
        self.assertTrue(shipment_advice)
        self.assertEqual(shipment_advice.planned_pickings_count, 3)
        self.assertEqual(shipment_advice.shipment_type, "outgoing")
        self.assertEqual(shipment_advice.warehouse_id, self.wh)
        self.assertEqual(shipment_advice.state, "done")
        self.assertEqual(shipment_advice.planned_picking_ids, self.pickings)
        self.assertEqual(shipment_advice.loaded_picking_ids, self.pickings)
        self.assertTrue(shipment_advice.in_release_channel_auto_process)
        self.assertSetEqual(set(self.pickings.mapped("state")), {"done"})
        self.assertEqual(self.channel.state, "delivered")
        return shipment_advice

    def test_01(self):
        shipment_advice = self.test_00()
        self.assertTrue(shipment_advice.in_release_channel_auto_process)
        action = self.channel.with_context(discard_logo_check=True).action_print()
        self.assertEqual(self.channel.state, "delivered")
        self.assertTrue(shipment_advice.in_release_channel_auto_process)
        self.assertEqual(action.get("type"), "ir.actions.report")
        self.assertEqual(
            action.get("report_name"), "shipment_advice.report_shipment_advice"
        )
        self.assertEqual(action.get("report_type"), "qweb-pdf")
        self.assertEqual(action.get("context").get("active_ids"), shipment_advice.ids)
        self.channel.action_sleep()
        self.assertEqual(self.channel.state, "asleep")
        self.assertFalse(shipment_advice.in_release_channel_auto_process)

    @mute_logger(
        "odoo.addons.stock_release_channel_shipment_advice_deliver.models.shipment_advice"
    )
    def test_02(self):
        """An error occurred while processing the shipment advices,.

        the print is not allowed
        """
        self.channel.dock_id = False
        with trap_jobs() as trap_rc:
            self.channel.action_deliver()
            self.assertEqual(self.channel.state, "delivering")
            trap_rc.assert_enqueued_job(self.channel._action_deliver)
            with trap_jobs() as trap_sa:
                trap_rc.perform_enqueued_jobs()
                shipment_advice = self.channel.shipment_advice_ids
                trap_sa.assert_enqueued_job(shipment_advice._auto_process)
                trap_sa.perform_enqueued_jobs()
        self.assertEqual(self.channel.state, "delivering_error")
        self.assertEqual(
            self.channel.delivering_error,
            f"An error occurred while processing:\n"
            f"- {shipment_advice.name}: Dock should be set on the shipment advice {shipment_advice.name}.",
        )
        self.assertEqual(self.channel.state, "delivering_error")
        with self.assertRaises(
            UserError, msg="Action 'Print' is not allowed for channel Default."
        ):
            self.channel.action_print()

    def test_03(self):
        """Re-deliver after fail then print."""
        self.test_02()
        self.assertEqual(self.channel.state, "delivering_error")
        self.channel.dock_id = self.dock
        self.test_00()
        self.assertEqual(self.channel.state, "delivered")
        # it should be two shipment_advices, one canceled and one done
        shipment_advices = self.channel.in_process_shipment_advice_ids
        self.assertEqual(len(shipment_advices), 1)
        self.assertTrue(shipment_advices.state, "done")
        action = self.channel.with_context(discard_logo_check=True).action_print()
        self.assertEqual(self.channel.state, "delivered")
        self.assertTrue(shipment_advices.in_release_channel_auto_process)
        self.assertTrue(shipment_advices.in_release_channel_auto_process)
        self.assertEqual(action.get("type"), "ir.actions.report")
        self.assertEqual(
            action.get("report_name"), "shipment_advice.report_shipment_advice"
        )
        self.assertEqual(action.get("report_type"), "qweb-pdf")
        # only the done shipment is printed
        self.assertEqual(action.get("context").get("active_ids"), shipment_advices.ids)
        self.channel.action_sleep()
        self.assertEqual(self.channel.state, "asleep")
        self.assertFalse(shipment_advices.in_release_channel_auto_process)
        self.assertFalse(shipment_advices.in_release_channel_auto_process)

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
        """Test action_delivering allowed."""
        self.channel.action_unlock()
        self.assertEqual(self.channel.state, "open")
        with self.assertRaises(
            UserError, msg="Action 'Delivering' is not allowed for channel Default."
        ):
            self.channel.action_delivering()

    def test_01(self):
        """Shipemnt advices are creared and automatically processed.

        The release channel
        is set to locked after it was delivered
        """

        with trap_jobs() as trap_rc:
            self.channel.action_delivering()
            self.assertEqual(self.channel.state, "delivering")
            trap_rc.assert_enqueued_job(self.channel._action_deliver)
            with trap_jobs() as trap_sa:
                trap_rc.perform_enqueued_jobs()
                shipment_advice = self.channel.shipment_advice_ids[-1]
                trap_sa.assert_enqueued_job(shipment_advice._auto_process)
                trap_sa.perform_enqueued_jobs()
        self.assertTrue(shipment_advice)
        self.assertEqual(shipment_advice.planned_pickings_count, 3)
        self.assertEqual(shipment_advice.shipment_type, "outgoing")
        self.assertEqual(shipment_advice.warehouse_id, self.wh)
        self.assertEqual(shipment_advice.state, "done")
        self.assertEqual(shipment_advice.planned_picking_ids, self.pickings)
        self.assertEqual(shipment_advice.loaded_picking_ids, self.pickings)
        self.assertSetEqual(set(self.pickings.mapped("state")), {"done"})
        self.assertEqual(self.channel.state, "delivered")
        self.channel.action_sleep()
        self.assertEqual(self.channel.state, "asleep")

    @mute_logger("odoo.addons.alc_stock_release_channel_deliver.models.shipment_advice")
    def test_02(self):
        """An error occurred while processing the shipment advices, the release channel.

        is notified and the error is logged
        """
        self.channel.dock_id = False
        with trap_jobs() as trap_rc:
            self.channel.action_delivering()
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
            f"An error occurred while processing the delivery automatically:\n"
            f"- {shipment_advice.name}: Dock should be set on the shipment advice {shipment_advice.name}.",
        )

    def test_03(self):
        """Re-deliver after fail."""
        self.test_02()
        self.assertEqual(self.channel.state, "delivering_error")
        self.channel.dock_id = self.dock
        self.test_01()

    def test_04(self):
        """No picking to deliver, an error should be raised."""
        self.pickings.write({"release_channel_id": False})
        with self.assertRaises(
            UserError, msg="No picking to deliver for channel Default"
        ):
            self.channel.action_delivering()

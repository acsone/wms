# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from vcr_unittest import VCRTestCase

from odoo.tools import mute_logger

from odoo.addons.queue_job.tests.common import trap_jobs
from odoo.addons.stock_release_channel.tests.common import ChannelReleaseCase


class TestShipmentAdvicePlannerToursolver(VCRTestCase, ChannelReleaseCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env.user.company_id.shipment_advice_run_in_queue_job = True
        cls.resource_1 = cls.env.ref(
            "shipment_advice_planner_toursolver.toursolver_resource_r1_demo"
        )
        cls.resource_2 = cls.env.ref(
            "shipment_advice_planner_toursolver.toursolver_resource_r2_demo"
        )
        cls.partner1 = cls.env.ref("base.res_partner_1")
        cls.partner2 = cls.env.ref("base.res_partner_2")
        cls.partner3 = cls.env.ref("base.res_partner_3")
        cls.picking.partner_id = cls.partner1
        cls.picking2.partner_id = cls.partner2
        cls.picking3.partner_id = cls.partner3
        cls.pickings = cls.picking + cls.picking2 + cls.picking3
        output_loc = cls.pickings.move_ids.location_id
        cls._update_qty_in_location(output_loc, cls.product1, 100)
        cls._update_qty_in_location(output_loc, cls.product2, 100)
        cls.pickings.move_ids.write({"procure_method": "make_to_stock"})
        cls.pickings.action_assign()
        cls.channel.picking_ids = cls.pickings
        cls.pickings.move_ids.write({"procure_method": "make_to_stock"})
        cls.pickings.action_assign()
        cls.channel.shipment_planning_method = "toursolver"
        cls.channel.delivery_resource_ids = cls.resource_1 | cls.resource_2
        cls.channel.action_lock()
        cls.dock = cls.env.ref("shipment_advice.stock_dock_demo")
        cls.channel.dock_id = cls.dock

    def test_00(self):
        """
        Success process:

            - The release channel plan the delivery
            - the delivery job call the shipment advice planner
            - the shipment advice planner create a toursolver task and plans its process
            - after the task is processed a shipment advice is created and job is planned
              to process it automatically
        """
        pickings = self.channel.picking_to_plan_ids
        with trap_jobs() as trap_rc:
            self.channel.action_deliver()
            self.assertEqual(self.channel.state, "delivering")
            trap_rc.assert_enqueued_job(self.channel._action_deliver)
            with trap_jobs() as trap_tt:
                trap_rc.perform_enqueued_jobs()
                self.assertFalse(self.channel.shipment_advice_ids)
                task = pickings.toursolver_task_id
                self.assertEqual(len(task), 1)
                self.assertEqual(task.state, "draft")
                trap_tt.assert_enqueued_job(task._toursolver_send_request)
                trap_tt.assert_enqueued_job(task._toursolver_check_status)
                trap_tt.assert_enqueued_job(task._toursolver_get_result)
                with trap_jobs() as trap_sa:
                    trap_tt.perform_enqueued_jobs()
                    shipment_advice = self.channel.shipment_advice_ids[-1]
                    trap_sa.assert_enqueued_job(shipment_advice._auto_process)
                    with trap_jobs() as trap_sap:
                        trap_sa.perform_enqueued_jobs()
                        trap_sap.perform_enqueued_jobs()
        self.assertTrue(shipment_advice)
        self.assertEqual(shipment_advice.toursolver_resource_id, self.resource_2)
        self.assertEqual(shipment_advice, task.shipment_advice_ids)
        self.assertEqual(shipment_advice.shipment_type, "outgoing")
        self.assertEqual(shipment_advice.state, "done")
        self.assertEqual(shipment_advice.planned_picking_ids, self.pickings)
        self.assertEqual(shipment_advice.loaded_picking_ids, self.pickings)
        self.assertSetEqual(set(self.pickings.mapped("state")), {"done"})
        self.assertEqual(self.channel.state, "delivered")

    @mute_logger(
        "odoo.addons.stock_release_channel_shipment_advice_deliver.models.shipment_advice"
    )
    @mute_logger(
        "odoo.addons.stock_release_channel_shipment_advice_deliver.models.toursolver_task"
    )
    @mute_logger("TourSolver Connexion")
    def test_01(self):
        """Connexion lost with toursolver, the toursolver task should notify the release.

        channel to set itself to delivering error
        """
        pickings = self.channel.picking_to_plan_ids
        with trap_jobs() as trap_rc:
            self.channel.action_deliver()
            self.assertEqual(self.channel.state, "delivering")
            trap_rc.assert_enqueued_job(self.channel._action_deliver)
            with trap_jobs() as trap_tt:
                trap_rc.perform_enqueued_jobs()
                self.assertFalse(self.channel.shipment_advice_ids)
                task = pickings.toursolver_task_id
                self.assertEqual(len(task), 1)
                self.assertEqual(task.state, "draft")
                trap_tt.assert_enqueued_job(task._toursolver_send_request)
                trap_tt.assert_enqueued_job(task._toursolver_check_status)
                trap_tt.assert_enqueued_job(task._toursolver_get_result)
                trap_tt.perform_enqueued_jobs()
        self.assertFalse(self.channel.shipment_advice_ids)
        self.assertEqual(task.state, "error")
        self.assertEqual(self.channel.state, "delivering_error")
        self.assertEqual(
            self.channel.delivering_error,
            "An error occurred while processing the delivery automatically:\n"
            f"- {task.display_name}: 403 Client Error:  for url: "
            "https://geoservices.geoconcept.com/ToursolverCloud/api/ts/toursolver/"
            "optimize?tsCloudApiKey=fake_api_key",
        )

    def test_03(self):
        """
        Error process:

            - The release channel plan the delivery
            - the delivery job call the shipment advice planner
            - the shipment advice planner create a toursolver task and plans its process
            - toursolver response indicate that one of the partners of the request is not
            planned
        """
        pickings = self.channel.picking_to_plan_ids
        with trap_jobs() as trap_rc:
            self.channel.action_deliver()
            self.assertEqual(self.channel.state, "delivering")
            trap_rc.assert_enqueued_job(self.channel._action_deliver)
            with trap_jobs() as trap_tt:
                trap_rc.perform_enqueued_jobs()
                self.assertFalse(self.channel.shipment_advice_ids)
                task = pickings.toursolver_task_id
                self.assertEqual(len(task), 1)
                self.assertEqual(task.state, "draft")
                trap_tt.assert_enqueued_job(task._toursolver_send_request)
                trap_tt.assert_enqueued_job(task._toursolver_check_status)
                trap_tt.assert_enqueued_job(task._toursolver_get_result)
                trap_tt.perform_enqueued_jobs()
        self.assertEqual(task.state, "error")
        self.assertEqual(self.channel.state, "delivering_error")
        self.assertEqual(
            self.channel.delivering_error,
            "An error occurred while processing the delivery automatically:\n"
            f"- {task.display_name}: The following partners are not found into the "
            f"optimization result: Wood Corner",
        )

# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV (https://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.addons.alc_shopfloor.tests.test_cluster_picking_unload import (
    ClusterPickingUnloadingCommonCase,
)
from odoo.addons.queue_job.job import Job


# pylint: disable=missing-return
class TestClusterPickingUnloadAsync(ClusterPickingUnloadingCommonCase):
    """Tests covering the /set_destination_all endpoint

    All the picked lines go to the same destination, a single call to this
    endpoint set them as "unloaded" and set the destination. When the last
    available line of a picking is unloaded, the picking is set to 'done'.
    """

    @classmethod
    def setUpComponent(cls):
        # setUpComponent is the first setup called by setupClass. We override it
        # to ensure that the env contains the required context to avoid trouble when
        # test are run with delivery_rounds installed.
        super(TestClusterPickingUnloadAsync, cls).setUpComponent()
        cls.env = cls.env(context=dict(cls.env.context, queue_job__no_delay=False))

    def test_set_destination_all_ok(self):
        """Set destination on all lines for the full batch and end the process"""
        self.env = self.env(context=dict(queue_job__no_delay=False))
        operations = self.pack_operation_ids
        # put destination packages, the whole quantity on lines and a similar
        # destination (when /set_destination_all is called, all the lines to
        # unload must have the same destination)
        self._set_dest_package_and_done(operations[:2], self.bin1)
        self._set_dest_package_and_done(operations[2:], self.bin2)
        operations.write({"location_dest_id": self.packing_location.id})
        jobs = self.env["queue.job"].sudo().search([])
        response = self.service.dispatch(
            "set_destination_all",
            params={
                "picking_batch_id": self.batch.id,
                "barcode": self.packing_location.barcode,
            },
        )
        self.assertRecordValues(self.batch, [{"state": "done"}])
        self.assert_response(
            response,
            next_state="start",
            message={"message_type": "success", "body": "Batch Transfer complete"},
        )
        # since the confirmation is async 2 jobs are created (1 by picking)
        jobs = self.env["queue.job"].sudo().search([]) - jobs
        self.assertEqual(2, len(jobs))
        # pickings are still assigned
        self.assertRecordValues(
            operations.mapped("picking_id"),
            [{"state": "assigned"}, {"state": "assigned"}],
        )
        # we perfor the jobs
        for job in jobs:
            job = Job.load(job.env, job.uuid)
            job.perform()
        # we expect all the pickings to be 'done'
        self.assertRecordValues(
            operations.mapped("picking_id"), [{"state": "done"}, {"state": "done"}]
        )
        self.assertRecordValues(
            operations,
            [
                {
                    "shopfloor_unloaded": True,
                    "qty_done": 10,
                    "state": "done",
                    "location_dest_id": self.packing_location.id,
                },
                {
                    "shopfloor_unloaded": True,
                    "qty_done": 10,
                    "state": "done",
                    "location_dest_id": self.packing_location.id,
                },
                {
                    "shopfloor_unloaded": True,
                    "qty_done": 10,
                    "state": "done",
                    "location_dest_id": self.packing_location.id,
                },
            ],
        )

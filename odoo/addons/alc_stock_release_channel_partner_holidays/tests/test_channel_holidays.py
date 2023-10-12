# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from freezegun import freeze_time

from odoo.addons.queue_job.job import Job
from odoo.addons.stock_release_channel.tests.common import ChannelReleaseCase


class AlcReleaseChannelHolidays(ChannelReleaseCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.schedule = cls.env["partner.scheduled.week"]
        default_values = {
            "partner_id": cls.delivery_address_1.id,
            "name": "Schedule 1",
            "start_date": "2023-01-27",
            "end_date": "2023-01-27",
        }
        return cls.schedule.create(default_values)

    @freeze_time("2023-01-27 10:00:00")
    def test_picking_scheduled_date(self):
        """
        There are three pickings that should be assigned to release channel.

        with three different partners.

        For picking 1, holidays have been setup today, so, it should have
        two pickings in the channel after assignation.
        """
        # Remove existing jobs as some already exists to assign pickings to channel
        jobs_before = self.env["queue.job"].search([])
        jobs_before.unlink()
        # Set the end time
        self.channel.process_end_time = 23.0
        # Asleep the release channel to void the process end date
        self.channel.action_sleep()
        self.channel.invalidate_recordset()
        self.channel.action_wake_up()
        # Execute the picking channel assignations
        jobs_after = self.env["queue.job"].search([])
        with self.assertLogs(
            "odoo.addons.alc_stock_release_channel_partner_holidays"
        ) as log:
            for job in jobs_after:
                job = Job.load(job.env, job.uuid)
                job.perform()
        pickings = self.channel.picking_ids
        self.assertEqual(2, len(pickings))
        self.assertEqual(self.picking2 | self.picking3, pickings)
        message = (
            "RELEASE CHANNEL: Some pickings have their partner in holidays: "
            + self.picking.name
        )
        self.assertIn(
            message,
            log.output[0],
        )

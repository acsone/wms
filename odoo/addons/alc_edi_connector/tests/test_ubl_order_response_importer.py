# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import base64

import mock
from odoo.addons.queue_job.job import Job

from .common import AlcEdiConnectorCase


class TestUblOrderResponseImporter(AlcEdiConnectorCase):
    @classmethod
    def setUpClass(cls):
        super(TestUblOrderResponseImporter, cls).setUpClass()
        cls.import_task_def = cls.edi_backend._get_task("ubl.order.response.importer")
        cls.OrderResponseImport = cls.env["order.response.import"]

    def test_01(self):
        """
        Data:
            No file found on the ftp sever
        Test case:
            Execute the task
        Expected result:
            No job created
        """
        job_counter = self.job_counter()
        self.mocked_sftp_pull.return_value = []
        self.import_task_def.execute()
        self.assertEqual(job_counter.count_created(), 0)

    def test_02(self):
        """
        Data:
            Files found on the ftp server
        Test Case:
            Execute the task
        Expected result:
            One job created by file found with the content link as attachment
        """
        job_counter = self.job_counter()
        self.mocked_sftp_pull.return_value = [
            ("PO1.xml", "content1"),
            ("PO2.xml", "content2"),
        ]
        self.import_task_def.execute()
        queue_jobs = job_counter.search_created()
        queue_jobs.sorted("id")
        self.assertEqual(len(queue_jobs), 2)
        attachment = self._get_attachments(queue_jobs[0])
        self.assertEqual(attachment.name, "PO1.xml")
        self.assertEqual(base64.decodestring(attachment.datas), "content1")
        attachment = self._get_attachments(queue_jobs[1])
        self.assertEqual(attachment.name, "PO2.xml")
        self.assertEqual(base64.decodestring(attachment.datas), "content2")

    def test_03(self):
        """
         Data:
            One File found on the ftp server
        Test Case:
            Execute the task
            Execute the job
        Expected result:
            One job created
            process_content method on "order.response.import" is called
            with the info read from the sftp server
        """
        job_counter = self.job_counter()
        self.mocked_sftp_pull.return_value = [("PO1.xml", "content1")]
        self.import_task_def.execute()
        queue_job = job_counter.search_created()
        self.assertEqual(len(queue_job), 1)
        attachment = self._get_attachments(queue_job)
        job = Job.load(self.env, queue_job.uuid)
        with mock.patch.object(
            self.OrderResponseImport.__class__, "process_attachment"
        ) as patched_process_content:
            job.perform()
            self.assertEqual(patched_process_content.call_count, 1)
            self.assertEqual(patched_process_content.call_args[0], (attachment,))

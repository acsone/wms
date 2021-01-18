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
        self.assertEqual(len(queue_jobs), 2)
        attachments = self._get_attachments(queue_jobs[0]) | self._get_attachments(
            queue_jobs[1]
        )
        result = {}
        for attachment in attachments:
            # remove pylint deprecated once on py3
            # pylint: disable=deprecated-method
            result[attachment.name] = base64.decodestring(attachment.datas)
        self.assertDictEqual({"PO1.xml": "content1", "PO2.xml": "content2"}, result)

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

# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import base64

import mock

from odoo.tools import file_open

from odoo.addons.purchase_order_import.wizard.order_response_import import (
    LINE_STATUS_ACCEPTED,
    ORDER_RESPONSE_STATUS_ACCEPTED,
)
from odoo.addons.purchase_order_import_ubl.wizard.order_response_import import (
    _ORDER_LINE_STATUS_TO_STATUS,
    _ORDER_RESPONSE_CODE_TO_STATUS,
)
from odoo.addons.queue_job.job import Job

from .common import AlcEdiConnectorCase

_STATUS_TO_RESPONSE_CODE = {p[1]: p[0] for p in _ORDER_RESPONSE_CODE_TO_STATUS.items()}

_STATUS_TO_LINE_STATUS = {p[1]: p[0] for p in _ORDER_LINE_STATUS_TO_STATUS.items()}


class TestUblOrderResponseImporter(AlcEdiConnectorCase):
    @classmethod
    def setUpClass(cls):
        super(TestUblOrderResponseImporter, cls).setUpClass()
        cls.import_task_def = cls.edi_backend._get_task("ubl.order.response.importer")
        cls.OrderResponseImport = cls.env["order.response.import"]
        with file_open("alc_edi_connector/tests/files/order_response1.xml", "rb") as f:
            cls.order_response_xml1 = f.read()

        with file_open("alc_edi_connector/tests/files/order_response2.xml", "rb") as f:
            cls.order_response_xml2 = f.read()

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

    def test_04(self):
        """
         Data:
        Test Case:
        Expected result:

        """

        xml_content1 = self.order_response_xml1.format(
            order_response_code=_STATUS_TO_RESPONSE_CODE[
                ORDER_RESPONSE_STATUS_ACCEPTED
            ],
            order_id=self.purchase_order.name,
            line_1_id=self.line1.id,
            line_1_qty=self.line1.product_qty,
            line_1_backorder_qty=0,
            line_1_status_code=_STATUS_TO_LINE_STATUS[LINE_STATUS_ACCEPTED],
            line_2_id=self.line2.id,
            line_2_qty=self.line2.product_qty,
            line_2_backorder_qty=0,
            line_2_status_code=_STATUS_TO_LINE_STATUS[LINE_STATUS_ACCEPTED],
        )

        xml_content2 = self.order_response_xml2.format(
            order_response_code=_STATUS_TO_RESPONSE_CODE[
                ORDER_RESPONSE_STATUS_ACCEPTED
            ],
            order_id=self.purchase_order.name,
            line_1_id=self.line1.id,
            line_1_qty=self.line1.product_qty,
            line_1_backorder_qty=0,
            line_1_status_code=_STATUS_TO_LINE_STATUS[LINE_STATUS_ACCEPTED],
            line_2_id=self.line2.id,
            line_2_qty=self.line2.product_qty,
            line_2_backorder_qty=0,
            line_2_status_code=_STATUS_TO_LINE_STATUS[LINE_STATUS_ACCEPTED],
        )

        attachment_in = self.env["ir.attachment"].create(
            {
                "name": "order_response1.xml",
                "datas": base64.b64encode(xml_content1),
                "datas_fname": "order_response1.xml",
            }
        )

        attachment_in2 = self.env["ir.attachment"].create(
            {
                "name": "order_response2.xml",
                "datas": base64.b64encode(xml_content2),
                "datas_fname": "order_response2.xml",
            }
        )
        self.env["order.response.import"].process_attachment(attachment_in)
        attachment_out1 = self.env["ir.attachment"].search(
            [
                ("name", "=", "order_response1.xml"),
                ("res_id", "=", self.purchase_order.id),
            ]
        )
        self.assertTrue(attachment_out1)

        message = self.env["order.response.import"].process_attachment(attachment_in2)
        self.assertEqual(
            message,
            "Purchase Order has already been modified by a previous Order response.",
        )
        # However, the second order response is still attached to the PO and a message is added in notes
        attachment_out2 = self.env["ir.attachment"].search(
            [
                ("name", "=", "order_response2.xml"),
                ("res_id", "=", self.purchase_order.id),
            ]
        )
        self.assertTrue(attachment_out2)

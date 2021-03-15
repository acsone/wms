# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import base64

import mock

from odoo import fields
from odoo.tools import file_open

from odoo.addons.queue_job.job import Job

from .common import AlcEdiConnectorCase


class TestUblDespatchAdviceImporter(AlcEdiConnectorCase):
    @classmethod
    def setUpClass(cls):
        super(TestUblDespatchAdviceImporter, cls).setUpClass()
        cls.import_task_def = cls.edi_backend._get_task("ubl.despatch.advice.importer")
        cls.DespatchAdviceImport = cls.env["despatch.advice.import"]
        with file_open(
            "alc_edi_connector/tests/files/despatch_advice_tmpl.xml", "rb"
        ) as f:
            cls.despatch_advice_xml1 = f.read()

        with file_open(
            "alc_edi_connector/tests/files/despatch_advice_2.xml", "rb"
        ) as f:
            cls.despatch_advice_xml2 = f.read()

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
            ("DespatchAdvice1.xml", "content1"),
            ("DespatchAdvice2.xml", "content2"),
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
        self.assertDictEqual(
            {"DespatchAdvice1.xml": "content1", "DespatchAdvice2.xml": "content2"},
            result,
        )

    def test_03(self):
        """
         Data:
            One File found on the ftp server
        Test Case:
            Execute the task
            Execute the job
        Expected result:
            One job created
            process_content method on "odespatch.advice.import" is called
            with the info read from the sftp server
        """
        job_counter = self.job_counter()
        self.mocked_sftp_pull.return_value = [("DespatchAdvice1.xml", "content1")]
        self.import_task_def.execute()
        queue_job = job_counter.search_created()
        self.assertEqual(len(queue_job), 1)
        attachment = self._get_attachments(queue_job)
        job = Job.load(self.env, queue_job.uuid)
        with mock.patch.object(
            self.DespatchAdviceImport.__class__, "process_attachment"
        ) as patched_process_content:
            job.perform()
            self.assertEqual(patched_process_content.call_count, 1)
            self.assertEqual(patched_process_content.call_args[0], (attachment,))

    def test_04(self):
        """
        Data: process DespatchAdvice
        Test case: Check that after updating PO, the DO is attatched to
        Expected result: We retrieve the DO at the PO level
        """
        xml_content = self.despatch_advice_xml1.format(
            order_id=self.purchase_order.name,
            line_1_id=self.line1.id,
            line_1_qty=self.line1.product_qty,
            line_1_product_ref=self.product_1.default_code,
            line_1_backorder_qty=12,
            line_2_id=self.line2.id,
            line_2_qty=self.line2.product_qty,
            line_2_product_ref=self.product_2.default_code,
            line_2_backorder_qty=0,
        )

        attachment_in = self.env["ir.attachment"].create(
            {
                "name": "despatch_advice_tmpl.xml",
                "datas": base64.b64encode(xml_content),
                "datas_fname": "despatch_advice_tmpl.xml",
            }
        )

        self.env["despatch.advice.import"].process_attachment(attachment_in)
        attachment_out = self.env["ir.attachment"].search(
            [
                ("name", "=", "despatch_advice_tmpl.xml"),
                ("res_id", "=", self.purchase_order.id),
            ]
        )
        self.assertTrue(attachment_out)

    def test_05(self):
        """
        Data: process DespatchAdvice
        Test case: Check that after updating PO, the DO is attatched to
        Expected result: We retrieve the DO at the PO level
        """

        self.product_3 = self.env["product.product"].create(
            {
                "name": "Product 1",
                "seller_ids": [
                    (0, 0, {"name": self.supplier.id, "product_code": "P3"})
                ],
            }
        )
        self.product_4 = self.env["product.product"].create(
            {
                "name": "Product 2",
                "seller_ids": [
                    (0, 0, {"name": self.supplier.id, "product_code": "P4"})
                ],
            }
        )

        self.purchase_order2 = self.env["purchase.order"].create(
            {
                "partner_id": self.supplier.id,
                "date_order": fields.Datetime.now(),
                "date_planned": fields.Datetime.now(),
                "currency_id": self.currency_euro.id,
            }
        )
        self.purchase_order3 = self.env["purchase.order"].create(
            {
                "partner_id": self.supplier.id,
                "date_order": fields.Datetime.now(),
                "date_planned": fields.Datetime.now(),
                "currency_id": self.currency_euro.id,
            }
        )
        self.line3 = self.purchase_order2.order_line.create(
            {
                "order_id": self.purchase_order2.id,
                "product_id": self.product_3.id,
                "name": self.product_3.name,
                "date_planned": fields.Datetime.now(),
                "product_qty": 10,
                "product_uom": self.env.ref("product.product_uom_unit").id,
                "price_unit": 15,
            }
        )
        self.line4 = self.purchase_order3.order_line.create(
            {
                "order_id": self.purchase_order3.id,
                "product_id": self.product_4.id,
                "name": self.product_4.name,
                "date_planned": fields.Datetime.now(),
                "product_qty": 5,
                "product_uom": self.env.ref("product.product_uom_unit").id,
                "price_unit": 25,
            }
        )
        self.purchase_order2.button_approve()
        self.purchase_order3.button_approve()

        xml_content = self.despatch_advice_xml2.format(
            line_1_id=self.line3.id,
            line_1_qty=self.line3.product_qty,
            line_1_product_ref=self.product_3.default_code,
            line_1_order_id=self.purchase_order2.name,
            line_1_backorder_qty=0,
            line_2_id=self.line4.id,
            line_2_qty=self.line4.product_qty,
            line_2_order_id=self.purchase_order3.name,
            line_2_product_ref=self.product_4.default_code,
            line_2_backorder_qty=0,
        )

        attachment_in = self.env["ir.attachment"].create(
            {
                "name": "despatch_advice_2.xml",
                "datas": base64.b64encode(xml_content),
                "datas_fname": "despatch_advice_2.xml",
            }
        )

        self.env["despatch.advice.import"].process_attachment(attachment_in)
        attachment_out1 = self.env["ir.attachment"].search(
            [
                ("name", "=", "despatch_advice_2.xml"),
                ("res_id", "=", self.purchase_order2.id),
            ]
        )
        self.assertTrue(attachment_out1)
        attachment_out2 = self.env["ir.attachment"].search(
            [
                ("name", "=", "despatch_advice_2.xml"),
                ("res_id", "=", self.purchase_order3.id),
            ]
        )
        self.assertTrue(attachment_out2)

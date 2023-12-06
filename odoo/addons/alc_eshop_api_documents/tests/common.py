# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging
from datetime import datetime, timedelta

from odoo.tools import mute_logger

from odoo.addons.alc_documents.tests.common import TestAlcDocuments
from odoo.addons.fastapi.tests.common import FastAPITransactionCase

from ..routers import documents_router


class TestDocumentsService(FastAPITransactionCase, TestAlcDocuments):
    @classmethod
    @mute_logger("odoo.addons.queue_job.utils")
    def setUpClass(cls):
        super().setUpClass()
        cls.default_fastapi_router = documents_router
        vals_partner = {"name": "P", "ref": "1214"}
        cls.partner = cls.env["res.partner"].create(vals_partner)
        cls.product = cls.env["product.product"].create({"name": "Product"})

        cls.alc_document_model = cls.env["alc.document"]

        cls.so_model = cls.env["sale.order"]
        cls.so_model_no_delay = cls.so_model.with_context(queue_job__no_delay=True)

        cls.partner_other = cls.env["res.partner"].create({"name": "Other"})

        # create a partner document
        vals_sale_order = cls._get_vals_sale_order()
        vals_sale_order["sale_channel_id"] = cls.env.ref(
            "alc_sale_channel.sale_channel_phone"
        ).id
        sale_order = cls.so_model_no_delay.create(vals_sale_order)
        sale_order.action_confirm()
        sale_order.env["ir.attachment"].create(
            {
                "type": "binary",
                "res_model": sale_order._name,
                "res_id": sale_order.id,
                "name": "test.pdf",
                "mimetype": "application/pdf",
                "raw": b"data",
            }
        )

        cls.yesterday = (datetime.now() - timedelta(days=1)).isoformat()
        cls.tomorrow = (datetime.now() + timedelta(days=1)).isoformat()

    def setUp(self):
        super().setUp()
        loggers = ["odoo.addons.queue_job.utils"]
        for logger in loggers:
            logging.getLogger(logger).addFilter(self)

        @self.addCleanup
        def un_mute_logger():
            for logger_ in loggers:
                logging.getLogger(logger_).removeFilter(self)

    def filter(self, record):
        return 0

# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo.tests.common import TransactionCase
from odoo.tools import mute_logger


class TestAlcDocuments(TransactionCase):
    @classmethod
    def _get_vals_sale_line(cls, product=None):
        return {
            "name": product.name,
            "product_id": product.id,
            "product_uom_qty": 1,
            "product_uom": product.uom_id.id,
            "price_unit": 10,
        }

    @classmethod
    def _get_vals_sale_order(cls, partner=None, products=None):
        products = products or cls.product
        return {
            "partner_id": (partner or cls.partner).id,
            "order_line": [(0, 0, cls._get_vals_sale_line(p)) for p in products],
        }

    @classmethod
    @mute_logger("odoo.addons.queue_job.models.base")
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        vals_partner = {"name": "P", "ref": "1214"}
        cls.partner = cls.env["res.partner"].create(vals_partner)
        cls.product = cls.env["product.product"].create({"name": "Product"})

        cls.alc_document_model = cls.env["alc.document"]

        cls.so_model = cls.env["sale.order"]
        cls.so_model_no_delay = cls.so_model.with_context(queue_job__no_delay=True)

    def setUp(self):
        super().setUp()
        loggers = ["odoo.addons.queue_job.models.base"]
        for logger in loggers:
            logging.getLogger(logger).addFilter(self)

        @self.addCleanup
        def un_mute_logger():
            for logger_ in loggers:
                logging.getLogger(logger_).removeFilter(self)

    def filter(self, record):
        return 0

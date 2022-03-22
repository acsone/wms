# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from odoo.addons.sale_cart_rest_api.tests.common import TestSaleCartRestApiCase


class TestSaleCartRestApi(TestSaleCartRestApiCase):
    @classmethod
    def setUpClass(cls):
        super(TestSaleCartRestApi, cls).setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, test_queue_job_no_delay=True))
        with cls.cart_service(cls.partner_1.id) as cart:
            info = cart.sync(
                uuid=None,
                transactions=[
                    {"uuid": "uuid1", "product_id": cls.product_1.id, "quantity": 1}
                ],
            )
            cls.cart = cart
            cls.so = cls.env["sale.order"].browse(info["id"])

    def setUp(self):
        super(TestSaleCartRestApi, self).setUp()
        # mute logger
        loggers = ["odoo.addons.queue_job.models.base"]
        for logger in loggers:
            logging.getLogger(logger).addFilter(self)

        # pylint: disable=unused-variable
        @self.addCleanup
        def un_mute_logger():
            for logger_ in loggers:
                logging.getLogger(logger_).removeFilter(self)

    def filter(self, record):
        # required to mute logger
        return 0

    def test_confirm(self):
        info = self.cart.dispatch(
            "confirm",
            params={"uuid": self.so.uuid, "customer_ref": "my_ref", "note": "my note"},
        )
        self.assertEqual("sale", self.so.state)
        self.assertEqual("my_ref", self.so.client_order_ref)
        self.assertEqual("my note", self.so.note)
        self.assertTrue(info)
        self.assertEqual("sale", info["state"])
        self.assertEqual("my_ref", info["customer_ref"])
        self.assertEqual("my note", info["note"])

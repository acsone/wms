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
                    {"uuid": "uuid1", "product_id": cls.product_1.id, "qty": 1}
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

    def test_get_next_suite_name(self):
        # not suite_name for cart without meds
        info = self.cart.dispatch("get_next_suite_name")
        self.assertEqual(None, info["value"])
        # only for cart with meds
        self.product_1.categ_id = self.env.ref("alc_product_category_data.product_categ_medoc")
        info = self.cart.dispatch("get_next_suite_name")
        self.assertEqual("1", info["value"])
        # if a suite_name is already on the cat, it's returned...
        self.so.suite_name = "my suite name"
        info = self.cart.dispatch("get_next_suite_name")
        self.assertEqual("my suite name", info["value"])

    def test_save_suite_name_on_confirm(self):
        info = self.cart.dispatch(
            "confirm", params={"uuid": self.so.uuid, "suite_name": "sn1"},
        )
        self.assertEqual("sn1", self.so.suite_name)
        self.assertEqual("sn1", info["suite_name"])

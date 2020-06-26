# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.connector_esb.tests import common


class ExportCustomerTestCase(common.ESBTestCase):
    @classmethod
    def setUpClass(cls):
        super(ExportCustomerTestCase, cls).setUpClass()
        cls.ResPartner = cls.env["res.partner"]
        cls.b2c_customer = cls.ResPartner.create(
            {
                "email": "joe@ch.ch",
                "name": "Joe",
                "customer": True,
                "is_b2c_customer": True,
            }
        )
        cls.timestamp = cls.env.ref("connector_esb.esb_timestamp_customer")

    def test_00(self):
        """
        Data:
            a B2C customer
        Test Case:
            Get customers to export
        Expected result:
            B2C customer is not into the items to export
        """
        self.timestamp.writer = "local"
        with self.backend.work_on(
            self.ResPartner._name, timestamp=self.timestamp
        ) as work:
            exporter = work.component(usage="record.exporter.cron")
            items = exporter.get_items(self.timestamp.last_export)
            self.assertNotIn(self.b2c_customer, items)

    def test_01(self):
        """
        Data:
            a B2C customer
        Test Case:
            Unset B2C customer
            Get customers to export
        Expected result:
            B2C customer is into the items to export
        """
        self.b2c_customer.is_b2c_customer = False
        with self.backend.work_on(
            self.ResPartner._name, timestamp=self.timestamp
        ) as work:
            exporter = work.component(usage="record.exporter.cron")
            items = exporter.get_items(self.timestamp.last_export)
            self.assertIn(self.b2c_customer, items)

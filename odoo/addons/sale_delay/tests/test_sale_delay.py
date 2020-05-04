# -*- coding: utf-8 -*-
# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from datetime import datetime

from freezegun import freeze_time
from odoo.tests.common import SavepointCase


class TestSaleDelay(SavepointCase):
    def setUp(self):
        super(TestSaleDelay, self).setUp()
        self.timeformat = "%Y-%m-%d %H:%M:%S"
        self.partner = self.env.ref("base.res_partner_1")
        self.partner.ref = "123321"
        # self.max_delay_for_sale_order_creation = 1
        self.so = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "date_order": "2019-10-10",
                # 'carrier_id': self.delivery.id,
                "client_order_ref": "whatever the client want",
                # 'delivery_price': 23.5,
                # 'suite_name': '0123434234',
                "order_line": [],
            }
        )

    @freeze_time("2019-10-01 12:00:00")
    def test_max_delay_not_set(self):
        """Check when no delay is set on the partner."""
        job_creation_time = datetime.strptime("2019-10-01 11:00:00", self.timeformat)
        self.assertEqual(self.so.is_delayed(job_creation_time), False)
        self.partner.max_delay_for_sale_order_creation = 0
        self.assertEqual(self.so.is_delayed(job_creation_time), False)

    @freeze_time("2019-10-01 12:00:00")
    def test_so_out_of_delay(self):
        """Check when no delay is set on the partner."""
        job_creation_time = datetime.strptime("2019-10-01 11:00:00", self.timeformat)
        self.partner.max_delay_for_sale_order_creation = 0.5
        self.assertEqual(self.so.is_delayed(job_creation_time), True)

    @freeze_time("2019-10-01 12:00:00")
    def test_so_in_time(self):
        """Check when no delay is set on the partner."""
        job_creation_time = datetime.strptime("2019-10-01 11:00:00", self.timeformat)
        self.partner.max_delay_for_sale_order_creation = 1
        self.assertEqual(self.so.is_delayed(job_creation_time), False)

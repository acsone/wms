# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from datetime import datetime, timedelta

from freezegun import freeze_time

from odoo.tests.common import TransactionCase


class TestSaleDelay(TransactionCase):
    @classmethod
    @freeze_time("2019-10-01 12:00:00")
    def setUpClass(cls):
        super().setUpClass()
        cls.timeformat = "%Y-%m-%d %H:%M:%S"
        cls.partner = cls.env.ref("base.res_partner_1")
        cls.partner.ref = "123321"
        cls.so = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "date_order": "2019-10-10",
                "client_order_ref": "whatever the client want",
                "order_line": [],
            }
        )

    @freeze_time(datetime.now() + timedelta(hours=1))
    def test_max_delay_not_set(self):
        """Check when no delay is set on the partner."""
        self.partner.auto_confirm_max_delay = 0
        self.so.action_confirm_and_check_delay()
        self.assertEqual(self.so.state, "sale")

    @freeze_time(datetime.now() + timedelta(hours=1))
    def test_so_out_of_delay(self):
        """Check when delay is set on the partner but exceeded."""
        self.so.message_ids.unlink()
        self.assertFalse(self.so.message_ids)
        self.partner.auto_confirm_max_delay = 0.5
        self.so.action_confirm_and_check_delay()
        self.assertEqual(self.so.state, "cancel")
        self.assertEqual(len(self.so.message_ids), 1)
        self.assertEqual(
            str(self.so.message_ids.body),
            "<p>Was automatically cancelled on creation because the job took longer to "
            "execute than the customer allows.</p>",
        )

    @freeze_time(datetime.now() + timedelta(hours=1))
    def test_so_in_time(self):
        """Check when delay is set on the partner but not exceeded."""
        self.partner.auto_confirm_max_delay = 1
        self.so.action_confirm_and_check_delay()
        self.assertEqual(self.so.state, "sale")

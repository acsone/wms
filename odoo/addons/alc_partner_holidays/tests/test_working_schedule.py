# Copyright 2019 Iryna Vyshnevska (Camptocamp)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from freezegun import freeze_time

from odoo.exceptions import ValidationError
from odoo.fields import Date
from odoo.tests.common import TransactionCase


class TestCustomerWorkingScheduleBase(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.schedule = cls.env["partner.scheduled.week"]
        cls.partner = cls.env["res.partner"].create(
            {"name": "Unittest partner", "ref": "12344566777878"}
        )
        cls.graphic_1 = cls.create_schedule()

    @classmethod
    def create_schedule(cls, vals=None):
        default_values = {
            "partner_id": cls.partner.id,
            "name": "Schedule 1",
            "start_date": "2019-01-01",
            "end_date": "2019-01-31",
        }
        if vals:
            default_values.update(vals)
        return cls.schedule.create(default_values)

    def test_allowed_day(self):

        # before start date schedule are not applied
        self.assertTrue(
            self.partner.is_shipping_date_allowed(Date.from_string("2018-05-05"))
        )
        # holidays are not allowed
        self.assertFalse(
            self.partner.is_shipping_date_allowed(Date.from_string("2019-01-01"))
        )
        self.assertFalse(
            self.partner.is_shipping_date_allowed(Date.from_string("2019-01-25"))
        )
        self.assertFalse(
            self.partner.is_shipping_date_allowed(Date.from_string("2019-01-31"))
        )
        # after end date schedule are not applied anymore
        self.assertTrue(
            self.partner.is_shipping_date_allowed(Date.from_string("2019-02-01"))
        )

    def test_contraint_overlap(self):
        error_msg = "You cannot have 2 schedules that overlap!"
        with self.assertRaises(ValidationError) as constraint_error:
            self.schedule.create(
                {
                    "partner_id": self.partner.id,
                    "name": "Schedule 1",
                    "start_date": "2019-01-01",
                    "end_date": "2019-01-31",
                }
            )
        self.assertEqual(error_msg, constraint_error.exception.name)

    def test_contraint_dates(self):
        error_msg = "The end date of a schedule must be after the start date or empty"
        with self.assertRaises(ValidationError) as constraint_error:
            self.schedule.create(
                {
                    "partner_id": self.partner.id,
                    "name": "Schedule 1",
                    "start_date": "2020-02-01",
                    "end_date": "2020-01-31",
                }
            )
        self.assertEqual(error_msg, constraint_error.exception.name)

    def test_void_date(self):
        # A void date should use today as reference date
        with freeze_time("2018-05-05"):
            self.assertTrue(self.partner.is_shipping_date_allowed(False))
        # holidays are not allowed
        with freeze_time("2019-01-01"):
            self.assertFalse(self.partner.is_shipping_date_allowed(False))

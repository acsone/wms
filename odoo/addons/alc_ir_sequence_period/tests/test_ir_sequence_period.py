# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import date

from freezegun import freeze_time

from odoo import Command
from odoo.tests.common import TransactionCase


class TestIrSequencePeriod(TransactionCase):
    @classmethod
    @freeze_time("2022-10-01")
    def setUpClass(cls):
        super().setUpClass()
        cls.date_range_type = cls.env["date.range.type"].create(
            {
                "name": "Fiscal year",
                "autogeneration_count": 1,
                "autogeneration_unit": "0",  # generate one year in advance
                "duration_count": 1,
                "unit_of_time": "0",  # generate one year period
                "name_expr": "'%s/%s' % (date_start.strftime('%Y'), date_end.strftime('%Y'))",
            }
        )
        cls.first_date_range = cls.env["date.range"].create(
            {
                "name": "2020/2021",
                "type_id": cls.date_range_type.id,
                "date_start": "2020-10-01",
                "date_end": "2021-09-30",
            }
        )

        cls.env.company.fiscalyear_last_day = 30
        cls.env.company.fiscalyear_last_month = "9"
        cls.product_a = cls.env.ref("product.product_product_4")
        cls.partner_a = cls.env["res.partner"].create({"name": "partner_a"})
        cls.journal = cls.env["account.journal"].search(
            [("type", "=", "sale")], limit=1
        )

        cls.out_invoice = cls.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": cls.partner_a.id,
                "invoice_date": "2020-10-17",
                "invoice_line_ids": [
                    Command.create(
                        {
                            "product_id": cls.product_a.id,
                            "price_unit": 1000.0,
                            "quantity": 5,
                        }
                    )
                ],
            }
        )

    def _test_date_range(self, date_range, date_start: date, date_end: date):
        year_start = date_start.year
        year_end = date_end.year
        name = f"{year_start}/{year_end}"
        self.assertEqual(date_range.name, name)
        self.assertEqual(date_range.date_start, date_start)
        self.assertEqual(date_range.date_end, date_end)

    @freeze_time("2022-10-01")
    def test_0(self):
        self.date_range_type.autogenerate_ranges()
        date_ranges = self.env["date.range"].search(
            [("type_id", "=", self.date_range_type.id)]
        )
        self.assertSetEqual(
            set(date_ranges.mapped("name")),
            {"2020/2021", "2021/2022", "2022/2023", "2023/2024"},
        )
        date_range_21_22 = date_ranges.filtered(lambda d: d.name == "2021/2022")
        date_range_22_23 = date_ranges.filtered(lambda d: d.name == "2022/2023")
        date_range_23_24 = date_ranges.filtered(lambda d: d.name == "2023/2024")
        self._test_date_range(
            date_range_21_22, date_start=date(2021, 10, 1), date_end=date(2022, 9, 30)
        )
        self._test_date_range(
            date_range_22_23, date_start=date(2022, 10, 1), date_end=date(2023, 9, 30)
        )
        self._test_date_range(
            date_range_23_24, date_start=date(2023, 10, 1), date_end=date(2024, 9, 30)
        )

    def setUp(self):
        super().setUp()
        self.sequence = self.env["ir.sequence"].create(
            {
                "name": "Customer Invoices",
                "prefix": "INV/%(range_year)s/",
                "use_date_range": True,
                "padding": 5,
                "date_range_ids": [
                    Command.create({"date_from": "2020-10-01", "date_to": "2021-09-30"})
                ],
            }
        )
        self.refund_sequence = self.env["ir.sequence"].create(
            {
                "name": "Customer Invoices",
                "prefix": "RINV/%(range_year)s/",
                "use_date_range": True,
                "padding": 5,
                "date_range_ids": [
                    Command.create({"date_from": "2020-10-01", "date_to": "2021-09-30"})
                ],
            }
        )
        self.journal.write(
            {
                "sequence_id": self.sequence.id,
                "refund_sequence_id": self.refund_sequence.id,
                "refund_sequence": True,
            }
        )

    @freeze_time("2020-10-17")
    def test_1(self):
        self.assertEqual(self.sequence._next(), "INV/2020/00001")

    @freeze_time("2020-10-17")
    def test_2(self):
        self.sequence.use_end_date = True
        self.assertEqual(self.sequence._next(), "INV/2021/00001")

    @freeze_time("2021-10-17")
    def test_3(self):
        self.sequence.use_end_date = True
        self.assertEqual(len(self.sequence.date_range_ids), 1)
        self.assertEqual(self.sequence._next(), "INV/2022/00001")
        self.assertEqual(len(self.sequence.date_range_ids), 2)
        new_date_range = self.sequence.date_range_ids[1]
        self.assertEqual(new_date_range.date_from, date(2021, 10, 1))
        self.assertEqual(new_date_range.date_to, date(2022, 9, 30))

    @freeze_time("2020-10-17")
    def test_4(self):
        self.sequence.use_end_date = True
        self.assertEqual(self.out_invoice.name, "/")
        self.out_invoice.action_post()
        self.assertEqual(self.out_invoice.name, "INV/2021/00001")

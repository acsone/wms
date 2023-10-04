# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import date

from freezegun import freeze_time

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

from datetime import date

from dateutil.relativedelta import relativedelta

from odoo.tools.float_utils import float_compare

from .common import TestAverageSaleCommon


class TestAveragesale(TestAverageSaleCommon):
    def setUp(self):
        super().setUp()
        self.today = date.today()

    def test_average_sale_annual(self):
        quantity_1 = 40
        so_1 = self._create_so(self.product_1, quantity_1)
        quantity_2 = 30
        so_2 = self._create_so(self.product_1, quantity_2)
        quantity_3 = 20
        so_3 = self._create_so(self.product_1, quantity_3)
        quantity_4 = 10
        so_4 = self._create_so(self.product_1, quantity_4)
        quantity_5 = 5
        so_5 = self._create_so(self.product_2, quantity_5)

        so_1.date_order = self.today - relativedelta(years=1, days=1)
        so_2.date_order = self.today - relativedelta(years=1)
        so_3.date_order = self.today - relativedelta(days=1)
        so_4.date_order = self.today
        so_5.date_order = self.today - relativedelta(months=6)

        self.so.flush_model()
        expected_sale = (quantity_2 + quantity_3) / 12
        self.product_1._compute_average_sale()
        compare = float_compare(
            expected_sale, self.product_1.average_annual_sale, self.precision
        )
        self.assertEqual(0, compare)

    def test_average_sale_3_months(self):
        quantity_1 = 40
        so_1 = self._create_so(self.product_1, quantity_1)
        quantity_2 = 30
        so_2 = self._create_so(self.product_1, quantity_2)
        quantity_3 = 20
        so_3 = self._create_so(self.product_1, quantity_3)
        quantity_4 = 10
        so_4 = self._create_so(self.product_1, quantity_4)

        first_day_last_year = (date.today() - relativedelta(years=1)).replace(day=1)
        # order out of scope
        so_1.date_order = first_day_last_year - relativedelta(days=1)
        # orders in 3 months average sale same period last year
        so_2.date_order = first_day_last_year
        so_3.date_order = first_day_last_year + relativedelta(months=3, days=-1)
        # order out of the cope of 3 months average sale same period last year
        so_4.date_order = first_day_last_year + relativedelta(months=3)

        self.so.flush_model()
        expected_sale = (quantity_2 + quantity_3) / 3
        self.product_1._compute_average_sale()
        compare = float_compare(
            expected_sale, self.product_1.average_three_months_sale, self.precision
        )
        self.assertEqual(0, compare)

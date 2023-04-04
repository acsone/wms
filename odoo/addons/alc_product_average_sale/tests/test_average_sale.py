from datetime import date

from dateutil.relativedelta import relativedelta

from odoo.fields import Command
from odoo.tests import TransactionCase
from odoo.tools.float_utils import float_compare


class TestAveragesale(TransactionCase):
    @classmethod
    def _create_so(cls, product, quantity):
        so = cls.so.create(
            {
                "partner_id": cls.env.ref("base.res_partner_3").id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": product.id,
                            "product_uom_qty": quantity,
                        }
                    )
                ],
            }
        )
        so.action_confirm()
        return so

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product_1 = cls.env["product.product"].create({"name": "TEST_1"})
        cls.product_2 = cls.env["product.product"].create({"name": "TEST_2"})
        cls.precision = cls.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )
        cls.so = cls.env["sale.order"]

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
        so_1.date_order = first_day_last_year - relativedelta(days=1)
        so_2.date_order = first_day_last_year
        so_3.date_order = first_day_last_year + relativedelta(months=2, days=28)
        so_4.date_order = first_day_last_year + relativedelta(months=3)

        self.so.flush_model()
        expected_sale = (quantity_2 + quantity_3) / 3
        self.product_1._compute_average_sale()
        compare = float_compare(
            expected_sale, self.product_1.average_three_months_sale, self.precision
        )
        self.assertEqual(0, compare)

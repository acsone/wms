# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import date

from dateutil.relativedelta import relativedelta

from odoo.addons.alc_product_average_sale.tests.common import (
    TestAverageSaleCommon,
)


class TestProductNbDaysOutOfStock(TestAverageSaleCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product_3 = cls.env.ref("product.product_product_6")
        cls.mto_route = cls.env.ref("stock.route_warehouse0_mto")
        cls.mto_route.active = True

    def test_00(self):
        """Test initial context."""
        self.assertEqual(self.product_1.virtual_available, 0)
        self.assertEqual(self.product_1.nb_days_out_of_stock, 0)
        self.assertEqual(self.product_1.average_annual_sale, 0)
        self.assertEqual(self.product_3.virtual_available, 287)
        self.assertEqual(self.product_3.nb_days_out_of_stock, 0)
        self.assertEqual(self.product_3.average_annual_sale, 0)

    def test_01(self):
        """Test nb_days_out_of_stock available product."""
        so = self._create_so(self.product_3, 100)
        so.date_order = date.today() - relativedelta(months=6)
        self.so.flush_model()
        self.product_3._compute_average_consumption()
        self.assertEqual(self.product_3.virtual_available, 187)
        self.assertEqual(self.product_3.average_annual_sale, 8.33)
        self.assertEqual(self.product_3.nb_days_out_of_stock, 51)

    def test_02(self):
        """Test nb_days_out_of_stock non-available product."""
        so = self._create_so(self.product_1, 100)
        so.date_order = date.today() - relativedelta(months=6)
        self.so.flush_model()
        self.product_3._compute_average_consumption()
        self.assertEqual(self.product_1.virtual_available, -100)
        self.assertEqual(self.product_1.average_annual_sale, 8.33)
        self.assertEqual(self.product_1.nb_days_out_of_stock, -27)

    def test_03(self):
        """Test nb_days_out_of_stock for mto product."""
        self.product_3.route_ids |= self.mto_route
        so = self._create_so(self.product_3, 100)
        so.date_order = date.today() - relativedelta(months=6)
        self.so.flush_model()
        self.product_3._compute_average_consumption()
        self.assertEqual(self.product_3.virtual_available, 187)
        self.assertEqual(self.product_3.average_annual_sale, 8.33)
        self.assertEqual(self.product_3.nb_days_out_of_stock, 0)

    def test_04(self):
        """Test nb_days_out_of_stock for multi-variants product."""
        so = self._create_so(self.product_3, 100)
        so.date_order = date.today() - relativedelta(months=6)
        self.product_3.copy().product_tmpl_id = self.product_3.product_tmpl_id
        self.assertEqual(self.product_3.product_variant_count, 2)
        self.so.flush_model()
        self.product_3._compute_average_consumption()
        self.assertEqual(self.product_3.virtual_available, 187)
        self.assertEqual(self.product_3.average_annual_sale, 8.33)
        self.assertEqual(self.product_3.nb_days_out_of_stock, 0)

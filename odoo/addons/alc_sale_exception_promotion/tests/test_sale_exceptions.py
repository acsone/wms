# Copyright 2018 Camptocamp SA
# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from datetime import date, timedelta

from odoo.addons.alc_sale_exception.tests.common import TestSaleOrderExceptionCommon


class TestSaleOrderException(TestSaleOrderExceptionCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.current_module = "alc_sale_exception_promotion"
        cls.current_exception_ids = cls.get_module_exception_ids()
        cls.activate_module_exceptions_only()

        today = date.today()
        cls.supplier_info = cls.env["product.supplierinfo"].create(
            {
                "partner_id": cls.partner.id,
                "price": 10,
                "product_id": cls.prod1.id,
                "product_tmpl_id": cls.prod1.product_tmpl_id.id,
                "date_start": today - timedelta(days=2),
                "date_end": today + timedelta(days=2),
                "ratio_promotional_product": 4,
                "ratio_main_product": 5,
            }
        )

    def test_promotional_product_warning(self):
        rules = self.env["exception.rule"].search([("active", "=", 1)])
        rules.write({"active": 0})
        exception = self.env.ref("alc_sale_exception_promotion.warning_free_product")
        exception.active = True
        so1 = self.env["sale.order"].create(self.so1_vals)
        sol = so1.order_line[0]
        self.assertEqual(exception.description, sol.exception)

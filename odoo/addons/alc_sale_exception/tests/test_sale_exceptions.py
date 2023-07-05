# Copyright 2018 Camptocamp SA
# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)


from odoo.addons.alc_sale_exception_settings.tests.common import (
    TestSaleOrderExceptionCommon,
)


class TestSaleOrderException(TestSaleOrderExceptionCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.current_module = "alc_sale_exception"
        cls.current_exception_ids = cls.get_module_exception_ids()
        cls.activate_module_exceptions_only()

    def test_warning_text_from_rule(self):
        self.env["exception.rule"].create(
            {
                "model": "sale.order.line",
                "name": "Exception Warning Test",
                "code": "failed=True",
                "active": True,
                "description": "Text WARNING",
            }
        )
        so1 = self.env["sale.order"].create(self.so1_vals.copy())
        sol = so1.order_line[0]
        self.assertTrue(sol.name.endswith(sol.warning_text))

    def test_no_line_under_0(self):
        exception = self.env.ref("alc_sale_exception.no_line_under_0")
        exception.active = True
        self.prod1.list_price = -1
        so1 = self.env["sale.order"].create(self.so1_vals.copy())
        sol = so1.order_line[0]
        # the Exception is blocking... no warning text
        warning_text = exception.description
        self.assertFalse(sol.warning_text)
        self.assertFalse(sol.name.endswith(warning_text))
        self.assertEqual(sol.main_exception_id, exception)
        sol.price_unit = 1
        self.assertFalse(sol.warning_text)
        self.assertFalse(sol.name.endswith(warning_text))
        self.assertFalse(sol.main_exception_id)

    def test_no_line_at_zero(self):
        exception = self.env.ref("alc_sale_exception.no_line_at_zero")
        exception.active = True
        self.prod1.list_price = 0
        so1 = self.env["sale.order"].create(self.so1_vals.copy())
        sol = so1.order_line[0]
        # the Exception is blocking... no warning text
        warning_text = exception.description
        self.assertFalse(sol.warning_text)
        self.assertFalse(sol.name.endswith(warning_text))
        self.assertEqual(sol.main_exception_id, exception)

    def test_order_amount_minimum(self):
        exception = self.env.ref("alc_sale_exception.order_amount_minimum")
        exception.active = True
        self.prod1.list_price = 1
        so1 = self.env["sale.order"].create(self.so1_vals.copy())
        so1.action_confirm()
        self.assertEqual(so1.state, "draft")
        self.assertIn(exception, so1.exception_ids)

    def test_skip_non_blocking(self):
        exception = self.env.ref("alc_sale_exception.order_amount_minimum")
        exception.is_blocking = False
        exception.active = True
        self.prod1.list_price = 1
        so1 = self.env["sale.order"].create(self.so1_vals.copy())
        so1.action_confirm()
        self.assertEqual(so1.state, "draft")
        self.env["res.config.settings"].sudo().create(
            {"alc_sale_exception_non_blocking_as_exception": False}
        ).execute()
        so1.action_confirm()
        self.assertEqual(so1.state, "sale")

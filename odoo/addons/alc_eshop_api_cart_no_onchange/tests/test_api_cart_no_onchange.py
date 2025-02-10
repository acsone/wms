# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import itertools

from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestApiCartNoOnchange(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.sale_order_line = cls.env["sale.order.line"]
        cls.expected_methods = [
            "_onchange_only_one_vat",
            "_onchange_product_id_warning",
            "_onchange_product_packaging_id",
            "_onchange_service_product_uom_qty",
            "onchange_product_id_reset_discount",
        ]

    def test_expected_onchange_methods(self):
        declared_methods = self.sale_order_line._onchange_methods.values()
        for method in itertools.chain.from_iterable(declared_methods):
            methode_name = getattr(method, "__name__", None)
            if methode_name:
                self.assertIn(methode_name, self.expected_methods)

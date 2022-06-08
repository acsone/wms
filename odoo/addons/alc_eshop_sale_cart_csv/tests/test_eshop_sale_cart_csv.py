# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .common import TestSaleCartRestApiCsvCase


class TestSaleCartRestApiInfo(TestSaleCartRestApiCsvCase):
    def test_csv(self):
        first_line = ["suite", "ref", "mail@alcyonbelux.be", "note"]
        # one column had a trailing ';', meaning an empty column
        csv_lines = [first_line, ["sku", "2", ""], ["missing", "4"]]
        with self.cart_service(self.partner_1.id) as cart:
            result = cart._csv(csv_lines=csv_lines)

        so = self.env["sale.order"].browse(result["id"])
        self.assertEqual("ref", so.client_order_ref)
        self.assertEqual("note", so.note)
        self.assertEqual("suite", so.suite_name)
        self.assertEqual(self.product, so.order_line.product_id)
        self.assertEqual(2, so.order_line.product_uom_qty)
        self.assertTrue(so.import_warning_msg)
        self.assertIn("missing", so.import_warning_msg)
        self.assertIn("import_warning_msg", result)
        self.assertEqual(result["import_warning_msg"], so.import_warning_msg)

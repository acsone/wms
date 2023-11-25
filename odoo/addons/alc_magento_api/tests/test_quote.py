# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import io

from .common import TestFacadeCart


class TestQuote(TestFacadeCart):
    def test_quote(self):
        original_qty = self.so.order_line.product_uom_qty
        xml_rqst = """
        <quote>
            <order_reference>Test</order_reference>
            <serial_number>32345</serial_number>
            <email_address>toto@test.com</email_address>
            <comments>This is a test</comments>
            <item>
                <sku>ABC</sku>
                <qty>10</qty>
            </item>
        </quote>
        """
        quote_facade = self._get_service_facade("quote")
        _result, error, _location = quote_facade(data=xml_rqst)
        self.assertEqual(error, None)
        self.assertEqual(10 + original_qty, self.so.order_line.product_uom_qty)
        self.assertEqual("Test", self.so.client_order_ref)
        self.assertEqual("32345", self.so.suite_name)
        self.assertEqual("<p>This is a test</p>", self.so.note)

    def test_quote_csv(self):
        existing_cart = self.env["sale.order"].search([("typology", "=", "cart")])
        first_line = ["suite", "ref", "mail@alcyonbelux.be", "note"]
        # one column had a trailing ';', meaning an empty column
        csv_lines = [
            first_line,
            [self.product_sku_n.default_code, "2", ""],
            ["missing", "4"],
        ]
        # we write the lines into a csv file that will be passed to the FastAPI test client
        # the file is not a real file, it is a BytesIO object
        csv_content = "\r\n".join(";".join(line) for line in csv_lines)
        csv_file = io.BytesIO(csv_content.encode("utf-8"))
        quote_csv_facade = self._get_service_facade("quote-csv")
        _result, error, _location = quote_csv_facade(file=csv_file)
        so = self.env["sale.order"].search([("typology", "=", "cart")]) - existing_cart
        self.assertEqual(error, "<error>The product missing is not available</error>")
        self.assertEqual("ref", so.client_order_ref)
        self.assertEqual("<p>note</p>", so.note)
        self.assertEqual("suite", so.suite_name)
        self.assertEqual(self.product_sku_n, so.order_line.product_id)
        self.assertEqual(2, so.order_line.product_uom_qty)
        self.assertTrue(so.import_warning_msg)
        self.assertIn("missing", so.import_warning_msg)

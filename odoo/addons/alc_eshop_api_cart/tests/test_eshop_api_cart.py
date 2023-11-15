# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import io
from contextlib import contextmanager
from datetime import datetime

from freezegun import freeze_time

from odoo.exceptions import ValidationError

from .common import TestSaleCartRestApiInfoCase


class TestSaleCartRestApiInfo(TestSaleCartRestApiInfoCase):
    @contextmanager
    def _record_new_note_template(self, so):
        class _Result:
            new_mails = self.env["mail.mail"].browse()

        template = self.env.ref("alc_eshop_api_cart.sale_order_notify_note")
        subject = template._render_field("subject", so.ids)[so.id]
        domain = [("subject", "=", subject)]
        template.auto_delete = False
        all_mails = self.env["mail.mail"].search(domain)
        result = _Result()
        yield result
        result.new_mails = self.env["mail.mail"].search(domain) - all_mails

    def test_update(self):
        # ensure the api works when mixed with the native api
        with self._create_test_client() as test_client:
            response = test_client.post(
                "carts/info", json={"customer_ref": "my_ref", "note": "my note"}
            )
            self.assertEqual(200, response.status_code)
            self.assertEqual("my_ref", self.so.client_order_ref)
            self.assertEqual("<p>my note</p>", self.so.note)

            response = test_client.post(
                f"carts/{self.so.uuid}/info",
                json={"customer_ref": "my_other_ref", "note": "my other note"},
            )
            self.assertEqual(200, response.status_code)
            self.assertEqual("my_other_ref", self.so.client_order_ref)
            self.assertEqual("<p>my other note</p>", self.so.note)

    def test_confirm(self):
        date_order = datetime(2021, 1, 1, 7, 10, 0)
        self.so.date_order = date_order
        self.assertEqual(date_order, self.so.date_order)
        confirm_date = datetime(2021, 1, 1, 7, 20, 0)
        with freeze_time(confirm_date), self._create_test_client() as test_client:
            response = test_client.post(
                f"carts/{self.so.uuid}/confirm",
                json={"customer_ref": "my_ref", "note": "my note"},
            )

        self.assertEqual(200, response.status_code)
        info = response.json()

        self.assertEqual("sale", self.so.state)
        self.assertEqual("my_ref", self.so.client_order_ref)
        self.assertEqual("<p>my note</p>", self.so.note)
        self.assertTrue(info)
        self.assertIn(info["state"], ["processing", "sale"])
        self.assertEqual("my_ref", info["customer_ref"])
        self.assertEqual("<p>my note</p>", info["note"])
        self.assertEqual(confirm_date, self.so.date_order)

    def test_confirm_without_note_sent_mail(self):
        with self._record_new_note_template(
            self.so
        ) as result, self._create_test_client() as test_client:
            test_client.post(
                "carts/confirm",
                json={"uuid": self.so.uuid, "customer_ref": "my_ref", "note": ""},
            )
        new_mail = result.new_mails
        self.assertFalse(new_mail)

    def test_confirm_not_allowed(self):
        self.so.partner_id.eshop_ordering_allowed = False
        with self._create_test_client() as test_client:
            with self.assertRaises(ValidationError):
                test_client.post("carts/confirm", json={"uuid": self.so.uuid})

            self.so.partner_id.eshop_ordering_allowed = True
            response = test_client.post("carts/confirm", json={"uuid": self.so.uuid})
            self.assertEqual(200, response.status_code)

    def test_csv(self):
        # we create a csv file with 2 lines
        # the first line is the cart info
        # the second line is the product line
        # the third line is a line with an unknown sku
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
        with self._create_test_client() as test_client:
            # specify the file in the mimetype
            response = test_client.post(
                "carts/csv", files={"file": ("cart.csv", csv_file)}
            )
        self.assertEqual(200, response.status_code)
        info = response.json()
        so = self.env["sale.order"].browse(info["id"])
        self.assertEqual("ref", so.client_order_ref)
        self.assertEqual("<p>note</p>", so.note)
        self.assertEqual("suite", so.suite_name)
        self.assertEqual(self.product_sku_n, so.order_line.product_id)
        self.assertEqual(2, so.order_line.product_uom_qty)
        self.assertTrue(so.import_warning_msg)
        self.assertIn("missing", so.import_warning_msg)
        self.assertIn("import_warning_msg", info)
        self.assertEqual(info["import_warning_msg"], so.import_warning_msg)

    def test_get_next_suite_name(self):
        with self._create_test_client() as test_client:
            response = test_client.get("carts/next_suite_name")
            self.assertEqual(200, response.status_code, response.content)
            self.assertEqual(None, response.json()["value"])

            self.product_1.categ_id = self.env.ref(
                "alc_product_category_data.product_categ_medoc"
            )
            response = test_client.get("carts/next_suite_name")
            self.assertEqual(200, response.status_code, response.content)
            self.assertEqual("1", response.json()["value"])

            # if a suite_name is already on the cat, it's returned...
            self.so.suite_name = "my suite name"
            response = test_client.get("carts/next_suite_name")
            self.assertEqual(200, response.status_code, response.content)
            self.assertEqual("my suite name", response.json()["value"])

    def test_save_suite_name_on_confirm(self):
        with self._create_test_client() as test_client:
            response = test_client.post(
                f"carts/{self.so.uuid}/confirm",
                json={"customer_ref": "my_ref", "note": "my note", "suite_name": "sn1"},
            )
            self.assertEqual(200, response.status_code)
            self.assertEqual("sn1", self.so.suite_name)
            self.assertEqual("sn1", response.json()["suite_name"])

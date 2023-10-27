# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.alc_cerberus_utils import utils

from .common import TestDocumentsService


class TestDocumentsServiceFlow(TestDocumentsService):
    def test_search(self):
        with self._create_test_client(partner=self.partner) as test_client:
            response = test_client.get("/documents")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["size"], 1)

            response = test_client.get("/documents", params={"type": "invoice"})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["size"], 0)

            response = test_client.get("/documents", params={"type": "order"})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["size"], 1)

            response = test_client.get(
                "/documents", params={"from_date": self.yesterday}
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["size"], 1)

            response = test_client.get(
                "/documents", params={"from_date": self.tomorrow}
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["size"], 0)

            response = test_client.get("/documents", params={"to_date": self.yesterday})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["size"], 0)

            response = test_client.get("/documents", params={"to_date": self.tomorrow})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["size"], 1)

        with self._create_test_client(partner=self.partner_other) as test_client:
            response = test_client.get("/documents")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["size"], 0)

    def test_search_sale_channel(self):
        with self._create_test_client(partner=self.partner) as test_client:
            response = test_client.get("/documents", params={"sale_channel": "phone"})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["size"], 1)

            response = test_client.get("/documents", params={"sale_channel": "fax"})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["size"], 0)

    def test_search_document_with_false_values(self):
        domain_documents = self.alc_document_model.get_partner_domain(self.partner)
        document = self.alc_document_model.search(domain_documents)
        document.write({"sale_channel_id": False})
        document.attachment_id.write({"res_model": False})
        with self._create_test_client(partner=self.partner) as test_client:
            response = test_client.get("/documents")
            self.assertEqual(response.status_code, 200)
            result = response.json()
            self.assertEqual(result["size"], 1)
            self.assertEqual(None, result["data"][0]["sale_channel"])
            self.assertEqual(None, result["data"][0]["res_model"])

    def test_search_document_with_date(self):
        domain_documents = self.alc_document_model.get_partner_domain(self.partner)
        document = self.alc_document_model.search(domain_documents)
        value = utils.odoo_dt_to_dt_utc(document.document_date)
        expected_date = value.isoformat().replace("+00:00", "Z")
        with self._create_test_client(partner=self.partner) as test_client:
            response = test_client.get("/documents")
            self.assertEqual(response.status_code, 200)
            result = response.json()
            self.assertEqual(expected_date, result["data"][0]["document_date"])

    def test_download(self):
        domain_documents = self.alc_document_model.get_partner_domain(self.partner)
        document = self.alc_document_model.search(domain_documents)
        with self._create_test_client(partner=self.partner) as test_client:
            response = test_client.get(f"/documents/{document.id}/download")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.content, b"data")

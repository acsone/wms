# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields

from .common import TestDocumentsService


class TestDocumentsServiceFlow(TestDocumentsService):
    def test_search(self):
        with self.documents_service() as service:
            result = service.search()
            self.assertEqual(result["size"], 1)

            result = service.search(type="invoice")
            self.assertEqual(result["size"], 0)

            result = service.search(type="order")
            self.assertEqual(result["size"], 1)

            result = service.search(from_date=self.yesterday)
            self.assertEqual(result["size"], 1)

            result = service.search(from_date=self.tomorrow)
            self.assertEqual(result["size"], 0)

            result = service.search(to_date=self.yesterday)
            self.assertEqual(result["size"], 0)

            result = service.search(to_date=self.tomorrow)
            self.assertEqual(result["size"], 1)

        with self.documents_service(partner=self.partner_other) as service:
            result = service.search()
            self.assertEqual(result["size"], 0)

    def test_search_sale_channel(self):
        with self.documents_service() as service:
            result = service.search(sale_channel="phone")
            self.assertEqual(result["size"], 1)

            result = service.search(sale_channel="fax")
            self.assertEqual(result["size"], 0)

    def test_search_document_with_false_values(self):
        domain_documents = self.alc_document_model.get_partner_domain(self.partner)
        document = self.alc_document_model.search(domain_documents)
        document.write({"sale_channel": False})
        document.attachment_id.write({"res_model": False})
        with self.documents_service() as service:
            result = service.search()
            self.assertEqual(result["size"], 1)
            self.assertEqual(None, result["data"][0]["sale_channel"])
            self.assertEqual(None, result["data"][0]["res_model"])

    def test_search_document_with_date(self):
        domain_documents = self.alc_document_model.get_partner_domain(self.partner)
        document = self.alc_document_model.search(domain_documents)
        value = document.document_date
        value = fields.Datetime.from_string(value)
        value = fields.Datetime.context_timestamp(document, value)
        with self.documents_service() as service:
            result = service.search()
            self.assertEqual(value, result["data"][0]["document_date"])

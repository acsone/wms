# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

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

        with self.documents_service(partner=self.partner_other) as service:
            result = service.search()
            self.assertEqual(result["size"], 0)

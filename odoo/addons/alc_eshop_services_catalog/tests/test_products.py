# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from .common import TestCatalogService


class TestCatalogServiceFlow(TestCatalogService):
    def test_get_by_reference(self):
        reference = "8248538"
        with self.catalog_service(self.partner) as service:
            with self.mock_product_data():
                result = service.dispatch("get_by_reference", reference)
                self.assertEqual(result["reference"], reference)
                self.assertEqual(result["name"], "MATELAS FOAM DOGBED GRIS 120x100cm")

    def test_get_by_reference_not_found(self):
        reference = "doesnotexist"
        with self.catalog_service(self.partner) as service:
            with self.assertRaises(Exception):
                service.dispatch("get_by_reference", reference)

    def test_search(self):
        # for now this is essentially a useless test since we mocked the get_iterator
        # also size will be wrong since search_count is not mocked in sync
        with self.catalog_service(self.partner) as service:
            with self.mock_product_data():
                params = {"name__ilike": "ATELAS"}
                result = service.dispatch("search", params=params)
                self.assertEqual(len(result["data"]), 1)

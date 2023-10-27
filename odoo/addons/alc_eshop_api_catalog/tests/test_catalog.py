# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from .common import TestCatalogService


class TestCatalogServiceFlow(TestCatalogService):
    def test_get_by_reference(self):
        reference = "8248538"
        with self._create_test_client(partner=self.partner) as test_client:
            with self.mock_product_data():
                response = test_client.get(f"/catalog/{reference}")
                self.assertEqual(response.status_code, 200)
                result = response.json()
                self.assertEqual(result["reference"], reference)
                self.assertEqual(result["name"], "MATELAS FOAM DOGBED GRIS 120x100cm")

    def test_get_by_reference_not_found(self):
        reference = "doesnotexist"
        with self._create_test_client(partner=self.partner) as test_client:
            response = test_client.get(f"/catalog/{reference}")
            self.assertEqual(response.status_code, 404)

    def test_search(self):
        # for now this is essentially a useless test since we mocked the get_iterator
        # also size will be wrong since search_count is not mocked in sync
        with self._create_test_client(partner=self.partner) as test_client:
            with self.mock_product_data():
                params = {"name__ilike": "ATELAS"}
                response = test_client.get("/catalog", params=params)
                self.assertEqual(response.status_code, 200)
                result = response.json()
                self.assertEqual(len(result["data"]), 1)

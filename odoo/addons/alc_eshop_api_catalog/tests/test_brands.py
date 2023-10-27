# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from .common import TestBrandsService


class TestRegistrationServiceFlow(TestBrandsService):
    def test_get(self):
        _id = self.brand_1.id
        with self._create_test_client(partner=self.partner) as test_client:
            response = test_client.get(f"/brands/{_id}")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["id"], _id)
            self.assertEqual(response.json()["name"], "numbah 1")

    def test_search(self):
        with self._create_test_client(partner=self.partner) as test_client:
            search_param = "NUM"
            response = test_client.get("/brands", params={"name__ilike": search_param})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["size"], 2)

            search_param = "NUMBAH"
            response = test_client.get("/brands", params={"name__ilike": search_param})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["size"], 1)

            search_param = "NUMBAH"
            response = test_client.get("/brands", params={"name": search_param})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["size"], 0)

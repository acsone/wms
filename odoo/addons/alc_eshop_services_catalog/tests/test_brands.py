# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from .common import TestBrandsService


class TestRegistrationServiceFlow(TestBrandsService):
    def test_get(self):
        _id = self.brand_1.id
        with self.brands_service(self.partner) as service:
            result = service.dispatch("get", _id)
            self.assertEqual(result["id"], _id)
            self.assertEqual(result["name"], "numbah 1")

    def test_search(self):
        with self.brands_service(self.partner) as service:
            search_param = "NUM"
            result = service.dispatch("search", params={"name__ilike": search_param})
            self.assertEqual(result["size"], 2)

            search_param = "NUMBAH"
            result = service.dispatch("search", params={"name__ilike": search_param})
            self.assertEqual(result["size"], 1)

            search_param = "NUMBAH"
            result = service.dispatch("search", params={"name": search_param})
            self.assertEqual(result["size"], 0)

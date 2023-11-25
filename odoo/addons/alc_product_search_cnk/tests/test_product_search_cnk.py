# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from .common import TestSearchCnk


class TestSearchCnkFlow(TestSearchCnk):
    """These tests might break if there are so many products that searching on.

    something might go over the limit even before reaching the test examples.
    That would seem very unlikely though.
    """

    def test_search_222(self):
        results = self.model_product.name_search("222")

        self.assertTrue(self.figeac.product_variant_id.name_get()[0] in results)
        self.assertTrue(self.emilion.product_variant_id.name_get()[0] in results)
        self.assertFalse(self.beaujolais.product_variant_id.name_get()[0] in results)

    def test_search_666(self):
        results = self.model_product.name_search("666")

        self.assertTrue(self.beaujolais.product_variant_id.name_get()[0] in results)
        self.assertFalse(self.figeac.product_variant_id.name_get()[0] in results)
        self.assertFalse(self.emilion.product_variant_id.name_get()[0] in results)

    def test_search_88(self):
        results = self.model_product.name_search("88")

        self.assertTrue(self.figeac.product_variant_id.name_get()[0] in results)
        self.assertFalse(self.emilion.product_variant_id.name_get()[0] in results)
        self.assertFalse(self.beaujolais.product_variant_id.name_get()[0] in results)

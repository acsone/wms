# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.product_abc_classification.tests.common import (
    ABCClassificationLevelCase,
)


class TestAbcStorage(ABCClassificationLevelCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_00_abc_storage_update(self):
        """
        Ensures the `abc_storage` field matches the `abc_classification_product_level_ids` field.

        The expected value for `abc_storage` is the first product_level's name.

        Data:
            A product.
        Test Case:
            1. Test defautl value of `abc_storage`
            2. Assiociate the product with 2 product levels
            3. Unlink the first product level
        Expected:
            1. The default value of `abc_storage` is "b"
            2. The value of `abc_storage` is the name of the first product level
            3. The value of `abc_storage` is still the name of the first product level
        """
        # 1
        self.assertEqual(self.product_product.abc_storage, "b")

        # 2
        product_level_1 = self.ProductLevel.create(
            {
                "product_id": self.product_product.id,
                "computed_level_id": self.classification_level_a.id,
                "profile_id": self.classification_profile.id,
            }
        )
        self.ProductLevel.create(
            {
                "product_id": self.product_product.id,
                "computed_level_id": self.classification_level_bis_b.id,
                "profile_id": self.classification_profile_bis.id,
            }
        )
        self.assertEqual(
            self.product_product.abc_storage,
            self.product_product.abc_classification_product_level_ids[0].level_id.name,
        )

        # 3
        product_level_1.unlink()
        self.assertEqual(
            self.product_product.abc_storage,
            self.product_product.abc_classification_product_level_ids[0].level_id.name,
        )

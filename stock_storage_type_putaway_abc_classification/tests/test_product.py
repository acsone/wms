# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .common import ABCClassificationLevelCase


class TestProduct(ABCClassificationLevelCase):
    def test_00(self):
        """
        Data:
            A product without level
        Test Case:
            1. Add a classification level A
            2. Set an new classification level B
            3. Remove the classification level
        Expected result:
            1 The computed field abc_storage is set to A
            2 The computed field abc_storage is set to B
            3 The computed field abc_storage is unset
        """
        self.assertFalse(self.product.abc_storage)
        # 1
        self._set_abc_level(self.product, self.classification_level_a)
        self.assertEqual(self.product.abc_storage, self.classification_level_a.name)
        # 2
        self._set_abc_level(self.product, self.classification_level_b)
        self.assertEqual(self.product.abc_storage, self.classification_level_b.name)
        # 3
        self.product.abc_classification_product_level_ids.unlink()
        self.assertFalse(self.product.abc_storage)

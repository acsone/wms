# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command

from odoo.addons.product_abc_classification.tests.common import (
    ABCClassificationLevelCase,
)


class TestAbcStorage(ABCClassificationLevelCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product_variant = cls._create_variant(cls.size_attr_value_s)

    def _are_abc_storage_fields_sync(self, product):
        """
        Returns True of the field `abc_storage` is the same as the first abc.

        classification product level.
        """
        return (
            product.abc_storage
            == product.abc_classification_product_level_ids[0].level_id.name
        )

    def test_abc_storage_update_product(self):
        """
        Tests the synchronization of the `abc_storage` computed field on `product.product`.

        with the primary ABC classification level from its associated `abc_classification_product_level_ids`.

        Data:
            A product from a template with 2 variants.
        Test Case:
            0. The template of the product used for this test has 2 variants
            1. Test default value of `abc_storage`
            2. Associate the product with 2 product levels
            3. Unlink the first product level
        Expected:
            0. Two variants for the test product template
            1. The default value of `abc_storage` is "b"
            2. The value of `abc_storage` is the name of the first product level
            3. The value of `abc_storage` is still the name of the first product level
        """
        # 0
        self.assertEqual(
            len(self.product_product.product_tmpl_id.product_variant_ids),
            2,
            "The tested product should have 2 variants",
        )

        # 1
        self.assertEqual(
            self.product_product.abc_storage,
            "b",
            "Unexpected default value for `abc_storage`.",
        )

        # 2
        self.product_product.abc_classification_product_level_ids = [
            Command.create(
                {
                    "product_id": self.product_product.id,
                    "computed_level_id": self.classification_level_a.id,
                    "profile_id": self.classification_profile.id,
                }
            ),
            Command.create(
                {
                    "product_id": self.product_product.id,
                    "computed_level_id": self.classification_level_bis_b.id,
                    "profile_id": self.classification_profile_bis.id,
                }
            ),
        ]
        product_levels = self.product_product.abc_classification_product_level_ids

        self.assertTrue(
            self._are_abc_storage_fields_sync(self.product_product),
            "ABC fields not sync after adding 2 product levels.",
        )

        # 3
        self.product_product.abc_classification_product_level_ids = [
            Command.unlink(product_levels[0].id)
        ]
        self.assertTrue(
            self._are_abc_storage_fields_sync(self.product_product),
            "ABC fields not sync after removing first product level.",
        )

    def test_abc_storage_update_template(self):
        """
        Tests the value of the `abc_storage` field on the product.

        template in different scenarios.

        Data:
            A product template and its 2 product variants.
        Test Case:
            0. Set the same product level for both variants
            1. Change one of the products product level so that they are now distinct
        Expected:
            0. The `abc_storage` of the template should be the same as the variants
            1. The `abc_storage` of the template should be False
        """
        template = self.product_product.product_tmpl_id

        # 0
        self.product_product.abc_classification_product_level_ids = [
            Command.create(
                {
                    "product_id": self.product_product.id,
                    "computed_level_id": self.classification_level_a.id,
                    "profile_id": self.classification_profile.id,
                }
            ),
        ]
        self.product_variant.abc_classification_product_level_ids = [
            Command.create(
                {
                    "product_id": self.product_product.id,
                    "computed_level_id": self.classification_level_a.id,
                    "profile_id": self.classification_profile.id,
                }
            ),
        ]

        self.assertEqual(template.abc_storage, "a")

        # 1
        self.product_variant.abc_classification_product_level_ids = [
            Command.clear(),
            Command.create(
                {
                    "product_id": self.product_product.id,
                    "computed_level_id": self.classification_level_b.id,
                    "profile_id": self.classification_profile.id,
                }
            ),
        ]
        self.assertEqual(template.abc_storage, False)

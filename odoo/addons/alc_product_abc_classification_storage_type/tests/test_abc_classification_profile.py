# Copyright 2021-2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from .common import AlcAbcClassificationStorageTypeCommon


class TestAlcAbcClassificationStorageType(AlcAbcClassificationStorageTypeCommon):
    def test_product_profile(self):
        """
        Set the product 1 package type to pallet.

        Then, affect this package type to the profile ones.
        Product 1 should have the stock profile
        MTO shouldn't.

        Then, change the product package type to carboxes.
        Profiles should be void.
        """
        self.assertFalse(self.product_alc_1.abc_classification_profile_ids)
        self.assertFalse(
            self.product_alc_1.product_tmpl_id.abc_classification_profile_ids
        )
        self.product_alc_1.product_tmpl_id.package_type_id = self.pallet_type
        self.stock_profile.package_type_ids |= self.pallet_type
        self.assertEqual(
            self.stock_profile, self.product_alc_1.abc_classification_profile_ids
        )
        self.assertEqual(
            self.stock_profile,
            self.product_alc_1.product_tmpl_id.abc_classification_profile_ids,
        )

        # Set the package type on the MTO product
        # Profile should not have been assigned
        self.product_alc_mto.product_tmpl_id.package_type_id = self.pallet_type
        self.assertFalse(self.product_alc_mto.abc_classification_profile_ids)

        self.product_alc_1.product_tmpl_id.package_type_id = self.cardboxes_type
        self.assertFalse(self.product_alc_1.abc_classification_profile_ids)

        self.stock_profile.package_type_ids |= self.cardboxes_type
        self.assertEqual(
            self.stock_profile, self.product_alc_1.abc_classification_profile_ids
        )

        self.profile_2.package_type_ids |= self.cardboxes_type
        self.assertEqual(
            (self.stock_profile | self.profile_2),
            self.product_alc_1.abc_classification_profile_ids,
        )

    def test_remove_package_type(self):
        """
        Set the product 1 package type to pallet.

        Then, affect this package type to the profile ones.
        Product 1 should have the stock profile
        MTO shouldn't.

        Then, change the product package type to carboxes.
        Profiles should be void.
        """
        self.assertFalse(self.product_alc_1.abc_classification_profile_ids)
        self.assertFalse(
            self.product_alc_1.product_tmpl_id.abc_classification_profile_ids
        )
        self.product_alc_1.product_tmpl_id.package_type_id = self.pallet_type
        self.stock_profile.package_type_ids |= self.pallet_type
        self.assertEqual(
            self.stock_profile, self.product_alc_1.abc_classification_profile_ids
        )
        self.stock_profile.package_type_ids = False
        self.assertFalse(self.product_alc_1.abc_classification_profile_ids)

    def test_product_profile_mto(self):
        """
        Set the stock profile to accept MTO products.

        Check MTO product has stock profile.
        """
        self.stock_profile.exclude_product_mto = False
        self.stock_profile.package_type_ids |= self.pallet_type
        self.product_alc_mto.product_tmpl_id.package_type_id = self.pallet_type
        self.assertEqual(
            self.stock_profile, self.product_alc_mto.abc_classification_profile_ids
        )
        self.assertEqual(
            self.stock_profile,
            self.product_alc_mto.product_tmpl_id.abc_classification_profile_ids,
        )

    def test_product_profile_sellable(self):
        """
        Set the stock profile to accept non sellable products.

        Change product to non sellable.
        Check product has stock profile.
        """
        self.stock_profile.exclude_non_sellable = False
        self.stock_profile.package_type_ids |= self.pallet_type
        self.product_alc_1.product_tmpl_id.package_type_id = self.pallet_type
        self.assertEqual(
            self.stock_profile, self.product_alc_1.abc_classification_profile_ids
        )
        self.assertEqual(
            self.stock_profile,
            self.product_alc_1.product_tmpl_id.abc_classification_profile_ids,
        )
        self.product_alc_1.product_tmpl_id.sale_ok = False
        self.assertEqual(
            self.stock_profile, self.product_alc_1.abc_classification_profile_ids
        )
        self.stock_profile.exclude_non_sellable = True
        self.assertFalse(self.product_alc_1.abc_classification_profile_ids)

# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .common import AclAbcClassificationProfilePickingZoneBase


class TestAbcClassificationProfile(AclAbcClassificationProfilePickingZoneBase):
    def test_00(self):
        """
        Data:
            1 product in zone medoc
            1 product in zone medoc + MTO
            1 product in zone aliment
            1 classification profile without picking_zone
        Test Case:
            1. Add zone medoc and zone alim to profile
            2. Remove the medoc zone from the profile
            3. Add zone medoc
            4. Includes product MTO
        Expected result:
            1. The two non MTO products are linked to the classification profile
            2. Only the product alim is still linked to the classification profile
            3. The two non MTO products are linked to the classification profile
            4. The mto product is linked
        """
        self.assertFalse(self.product_medoc.abc_classification_profile_ids)
        self.assertFalse(self.product_aliment.abc_classification_profile_ids)
        self.assertFalse(self.classification_profile.picking_zone_ids)
        # 1
        self.classification_profile.picking_zone_ids = self.zone_med | self.zone_ali
        self.assertEqual(
            self.product_medoc.abc_classification_profile_ids,
            self.classification_profile,
        )
        self.assertEqual(
            self.product_aliment.abc_classification_profile_ids,
            self.classification_profile,
        )
        self.assertFalse(self.product_medoc_mto.abc_classification_profile_ids)
        # 2
        self.classification_profile.picking_zone_ids = self.zone_ali
        self.assertFalse(self.product_medoc.abc_classification_profile_ids)
        self.assertEqual(
            self.product_aliment.abc_classification_profile_ids,
            self.classification_profile,
        )
        self.assertFalse(self.product_medoc_mto.abc_classification_profile_ids)
        # 3
        self.classification_profile.write({"picking_zone_ids": [(4, self.zone_med.id)]})
        self.assertEqual(
            self.product_medoc.abc_classification_profile_ids,
            self.classification_profile,
        )
        self.assertEqual(
            self.product_aliment.abc_classification_profile_ids,
            self.classification_profile,
        )
        self.assertFalse(self.product_medoc_mto.abc_classification_profile_ids)
        # 4
        self.classification_profile.exclude_product_mto = False
        self.assertEqual(
            self.product_medoc.abc_classification_profile_ids,
            self.classification_profile,
        )
        self.assertEqual(
            self.product_aliment.abc_classification_profile_ids,
            self.classification_profile,
        )
        self.assertEqual(
            self.product_medoc.abc_classification_profile_ids,
            self.classification_profile,
        )
        self.assertEqual(
            self.product_medoc_mto.abc_classification_profile_ids,
            self.classification_profile,
        )
        # remove mto
        self.classification_profile.exclude_product_mto = True
        self.assertEqual(
            self.product_medoc.abc_classification_profile_ids,
            self.classification_profile,
        )
        self.assertEqual(
            self.product_aliment.abc_classification_profile_ids,
            self.classification_profile,
        )
        self.assertFalse(self.product_medoc_mto.abc_classification_profile_ids)

    def test_01(self):
        """
        Data:
            1 product in zone medoc with sale_ok=False
        Test case:
            1. Add zone medoc and zone alim to profile
            2. set exclude non sellable to False
            3  set exclude non sellable to False
        Expected result:
            1. No profile on product
            2. Product linked to the profile
            3. No profile on product
        """
        self.product_medoc.sale_ok = False
        self.classification_profile.exclude_non_sellable = True
        self.assertFalse(self.product_medoc.abc_classification_profile_ids)
        # 1
        self.classification_profile.picking_zone_ids = self.zone_med
        self.assertFalse(self.product_medoc.abc_classification_profile_ids)
        # 2
        self.classification_profile.exclude_non_sellable = False
        self.assertEqual(
            self.product_medoc.abc_classification_profile_ids,
            self.classification_profile,
        )
        # 3
        self.classification_profile.exclude_non_sellable = True
        self.assertFalse(self.product_medoc.abc_classification_profile_ids)

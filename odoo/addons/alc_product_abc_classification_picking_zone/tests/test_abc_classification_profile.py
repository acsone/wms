# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .common import AclAbcClassificationProfilePickingZoneBase


class TestAbcClassificationProfile(AclAbcClassificationProfilePickingZoneBase):
    def test_00(self):
        """
        Data:
            1 product in zone medoc
            1 product in zone aliment
            1 classification profile without picking_zone
        Test Case:
            1. Add zone medoc and zone alim to profile
            2. Remove the medoc zone from the profile
            3. Add zone medoc
        Expected result:
            1. The two products are linked to the classification profile
            2. Only the product alim is still linked to the classification profile
            3. The two products are linked to the classification profile
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
        # 2
        self.classification_profile.picking_zone_ids = self.zone_ali
        self.assertFalse(self.product_medoc.abc_classification_profile_ids)
        self.assertEqual(
            self.product_aliment.abc_classification_profile_ids,
            self.classification_profile,
        )
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

# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .common import AclAbcClassificationProfilePickingZoneBase


class TestProduct(AclAbcClassificationProfilePickingZoneBase):
    def test_00(self):
        """
        Data:
            A template without route
            A classification profile without zone
        Test Case:
            1. Add picking zone medoc to the profile
            2. Add the medoc route to the template
            3. Remove the medoc route
        Expected result:
            1. No profile associated to template and variant
            2. Test profile associated to template and variant
            3. No profile associated to template and variant
        """
        template = self.no_route_product.product_tmpl_id
        self.assertFalse(template.abc_classification_profile_ids)
        self.assertFalse(self.no_route_product.abc_classification_profile_ids)
        # 1
        self.classification_profile.picking_zone_ids = self.zone_med
        self.assertFalse(template.abc_classification_profile_ids)
        self.assertFalse(self.no_route_product.abc_classification_profile_ids)
        # 2
        template.route_ids = self.route_medoc
        self.assertEqual(
            template.abc_classification_profile_ids, self.classification_profile
        )
        self.assertEqual(
            self.no_route_product.abc_classification_profile_ids,
            self.classification_profile,
        )
        # 3
        template.route_ids = False
        self.assertFalse(template.abc_classification_profile_ids)
        self.assertFalse(self.no_route_product.abc_classification_profile_ids)

    def test_01(self):
        """
        Data:
            A product variant without route
            A classification profile without zone
        Test Case:
            1. Add picking zone medoc to the profile
            2. Add the medoc route to the prod variant
            3. Remove the medoc route
        Expected result:
            1. No profile associated to template and variant
            2. Test profile associated to template and variant
            3. No profile associated to template and variant
        """
        template = self.no_route_product.product_tmpl_id
        self.assertFalse(template.abc_classification_profile_ids)
        self.assertFalse(self.no_route_product.abc_classification_profile_ids)
        # 1
        self.classification_profile.picking_zone_ids = self.zone_med
        self.assertFalse(template.abc_classification_profile_ids)
        self.assertFalse(self.no_route_product.abc_classification_profile_ids)
        # 2
        self.no_route_product.route_ids = self.route_medoc
        self.assertEqual(
            template.abc_classification_profile_ids, self.classification_profile
        )
        self.assertEqual(
            self.no_route_product.abc_classification_profile_ids,
            self.classification_profile,
        )
        # 3
        self.no_route_product.route_ids = False
        self.assertFalse(template.abc_classification_profile_ids)
        self.assertFalse(self.no_route_product.abc_classification_profile_ids)

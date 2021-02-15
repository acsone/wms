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

    def test_02(self):
        """
        Data:
            A mto product variant with route medoc
            A classification profile with zone medoc
            exclude_mto_product is True by default
        Test Case:
            1. set exclude_mto_product to False
            2. set exclude_mto_product to True
            3. remove route mto from template
            4. add route mto to template
        Expected result:
            1. Test profile associated to template and variant
            2. No profile associated to template and variant
            3. Test profile associated to template and variant
            4. No profile associated to template and variant
        """
        template = self.product_medoc_mto.product_tmpl_id
        self.classification_profile.picking_zone_ids = self.zone_med

        self.assertFalse(template.abc_classification_profile_ids)
        self.assertFalse(self.product_medoc_mto.abc_classification_profile_ids)
        self.assertTrue(template.is_mto_product)
        # 1
        self.classification_profile.exclude_product_mto = False
        self.assertEqual(
            template.abc_classification_profile_ids, self.classification_profile
        )
        self.assertEqual(
            self.product_medoc_mto.abc_classification_profile_ids,
            self.classification_profile,
        )
        # 2
        self.classification_profile.exclude_product_mto = True
        self.assertFalse(template.abc_classification_profile_ids)
        self.assertFalse(self.product_medoc_mto.abc_classification_profile_ids)
        # 3
        template.route_ids = self.route_medoc
        self.assertEqual(
            template.abc_classification_profile_ids, self.classification_profile
        )
        self.assertEqual(
            self.product_medoc_mto.abc_classification_profile_ids,
            self.classification_profile,
        )
        # 4
        template.route_ids = self.route_medoc | self.route_mto
        self.assertFalse(template.abc_classification_profile_ids)
        self.assertFalse(self.product_medoc_mto.abc_classification_profile_ids)

    def test_03(self):
        """
        Data:
            A mto product variant with route medoc
            A classification profile with zone medoc
            exclude_mto_product is True by default
        Test Case:
            1. set exclude_mto_product to False
            2. set exclude_mto_product to True
            3. remove route mto from variant
            4. add route mto to variant
        Expected result:
            1. Test profile associated to template and variant
            2. No profile associated to template and variant
            3. Test profile associated to template and variant
            4. No profile associated to template and variant
        """
        template = self.product_medoc_mto.product_tmpl_id
        self.classification_profile.picking_zone_ids = self.zone_med

        self.assertFalse(template.abc_classification_profile_ids)
        self.assertFalse(self.product_medoc_mto.abc_classification_profile_ids)
        self.assertTrue(template.is_mto_product)
        # 1
        self.classification_profile.exclude_product_mto = False
        self.assertEqual(
            template.abc_classification_profile_ids, self.classification_profile
        )
        self.assertEqual(
            self.product_medoc_mto.abc_classification_profile_ids,
            self.classification_profile,
        )
        # 2
        self.classification_profile.exclude_product_mto = True
        self.assertFalse(template.abc_classification_profile_ids)
        self.assertFalse(self.product_medoc_mto.abc_classification_profile_ids)
        # 3
        self.product_medoc_mto.route_ids = self.route_medoc
        self.assertEqual(
            template.abc_classification_profile_ids, self.classification_profile
        )
        self.assertEqual(
            self.product_medoc_mto.abc_classification_profile_ids,
            self.classification_profile,
        )
        # 4
        self.product_medoc_mto.route_ids = self.route_medoc | self.route_mto
        self.assertFalse(template.abc_classification_profile_ids)
        self.assertFalse(self.product_medoc_mto.abc_classification_profile_ids)

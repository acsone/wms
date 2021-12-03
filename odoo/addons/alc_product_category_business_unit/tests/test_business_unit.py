# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestBusinessUnit(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestBusinessUnit, cls).setUpClass()
        cls.ProductCategory = cls.env["product.category"]
        cls.business_unit_category = cls.ProductCategory.create(
            {"name": "Business Unit Category", "is_business_unit": True}
        )

        cls.sub_category = cls.ProductCategory.create(
            {"name": "Test", "parent_id": cls.business_unit_category.id}
        )

        cls.product1 = cls.env["product.product"].create({"name": "product test 1"})
        cls.product_template1 = cls.product1.product_tmpl_id

        cls.product_template2 = cls.env["product.template"].create(
            {"name": "product test 2"}
        )
        cls.product2 = cls.product_template2.product_variant_ids

    def test_00(self):
        """
        Data: business unit on product
        Test case: check that if we set the business unit on product, its propagated to the product template
        expected: business unit on product template

        """
        self.product1.categ_id = self.sub_category.id
        self.assertEqual(self.product1.business_unit_id, self.business_unit_category)
        self.assertEqual(
            self.product_template1.business_unit_id, self.business_unit_category
        )

    def test_01(self):
        """
        Data: business unit on product template
        Test case: check that if we set the business unit on product template, its propagated to the product
        expected: business unit on product

        """
        self.product_template2.categ_id = self.sub_category.id
        self.assertEqual(
            self.product_template2.business_unit_id, self.business_unit_category
        )
        self.assertEqual(self.product2.business_unit_id, self.business_unit_category)

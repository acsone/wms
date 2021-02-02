# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestProductDimensions(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestProductDimensions, cls).setUpClass()

        cls.product_template = cls.env["product.template"].create(
            {
                "name": "Unittest P1",
                "length": 10.0,
                "width": 5.0,
                "height": 3.0,
                "uom_id": cls.env.ref("product.product_uom_unit").id,
                "type": "consu",
            }
        )

        cls.product = cls.env["product.product"].create(
            {
                "name": "test product2",
                "default_code": "987654322",
                "tracking": "none",
                "list_price": 20,
                "length": 10.0,
                "width": 5.0,
                "height": 3.0,
                "uom_id": cls.env.ref("product.product_uom_unit").id,
            }
        )

    def test_00(self):
        """
        Data:
            one product template with dimensions
        Test Case:
            get the product associated to the product_template and check that the length, width and height
            are the same as for the product template
        Expected result:
            length, width, height are the same on the product and product template
        """

        product = self.product_template.product_variant_ids

        self.assertEqual(product.length, 10.0)
        self.assertEqual(product.width, 5.0)
        self.assertEqual(product.height, 3.0)

    def test_01(self):
        """
        Data:
            Update the dimensions on the product template
        Test Case:
            get the product associated to the product template and check that the length, width and height
            are the same as for the product template
        Expected result:
            length, width, height are the same on the product and product template
        """
        self.product_template.length = 20.0
        self.product_template.width = 12.0
        self.product_template.height = 1.5

        product = self.product_template.product_variant_ids

        self.assertEqual(product.length, 20.0)
        self.assertEqual(product.width, 12.0)
        self.assertEqual(product.height, 1.5)

    def test_02(self):
        """
        Data:
            one product with dimensions
        Test Case:
            get the product template associated to the product and check that the length, width and height
            are the same as for the product
        Expected result:
            length, width, height are the same on the product and product template
        """
        product_template = self.product.product_tmpl_id

        self.assertEqual(product_template.length, 10.0)
        self.assertEqual(product_template.width, 5.0)
        self.assertEqual(product_template.height, 3.0)

    def test_03(self):
        """
        Data:
            Update the dimensions on the product
        Test Case:
            get the product template associated to the product and check that the length, width and height
            are the same as for the product
        Expected result:
            length, width, height are the same on the product and product template
        """
        self.product.length = 8.0
        self.product.width = 3.0
        self.product.height = 30.0
        product_template = self.product.product_tmpl_id

        self.assertEqual(product_template.length, 8.0)
        self.assertEqual(product_template.width, 3.0)
        self.assertEqual(product_template.height, 30.0)

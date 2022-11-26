# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestProductDimensions(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.product_template = cls.env["product.template"].create(
            {
                "name": "Unittest P1",
                "product_length": 10.0,
                "product_width": 5.0,
                "product_height": 3.0,
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "type": "consu",
            }
        )

        cls.product = cls.env["product.product"].create(
            {
                "name": "test product2",
                "default_code": "987654322",
                "list_price": 20,
                "product_length": 10.0,
                "product_width": 5.0,
                "product_height": 3.0,
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
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

        self.assertEqual(product.product_length, 10.0)
        self.assertEqual(product.product_width, 5.0)
        self.assertEqual(product.product_height, 3.0)

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
        self.product_template.product_length = 20.0
        self.product_template.product_width = 12.0
        self.product_template.product_height = 1.5
        self.product_template.weight = 4.0

        product = self.product_template.product_variant_ids

        self.assertEqual(product.product_length, 20.0)
        self.assertEqual(product.product_width, 12.0)
        self.assertEqual(product.product_height, 1.5)
        self.assertEqual(product.weight, 4.0)

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

        self.assertEqual(product_template.product_length, 10.0)
        self.assertEqual(product_template.product_width, 5.0)
        self.assertEqual(product_template.product_height, 3.0)

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
        self.product.product_length = 8.0
        self.product.product_width = 3.0
        self.product.product_height = 30.0
        self.product.weight = 10.0
        product_template = self.product.product_tmpl_id

        self.assertEqual(product_template.product_length, 8.0)
        self.assertEqual(product_template.product_width, 3.0)
        self.assertEqual(product_template.product_height, 30.0)
        self.assertEqual(product_template.weight, 10.0)

# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestPackagingSearch(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ProductAttribute = cls.env["product.attribute"]
        cls.ProductAttributeValue = cls.env["product.attribute.value"]
        cls.attribute_color = cls.ProductAttribute.create(
            {"name": "Color", "sequence": 1}
        )

        # Product Attribute color Value
        cls.attribute_color_red = cls.ProductAttributeValue.create(
            {"name": "red", "attribute_id": cls.attribute_color.id, "sequence": 1}
        )
        cls.attribute_color_blue = cls.ProductAttributeValue.create(
            {"name": "blue", "attribute_id": cls.attribute_color.id, "sequence": 2}
        )
        cls.product = cls.env["product.template"].create(
            {
                "name": "One Variant Template",
            }
        )

        cls.packaging = cls.env["product.packaging"].create(
            {
                "name": "Packaging test",
                "product_id": cls.product.product_variant_ids.id,
            }
        )
        if "loyalty.program" in cls.env:
            cls.env["loyalty.program"].search([]).toggle_active()

    def test_packaging_search(self):
        # Deactivate existing products but the one just created
        self.env["product.template"].search([("id", "!=", self.product.id)]).write(
            {"active": False}
        )
        # The search on packagings should return the product that has one variant
        product = self.env["product.template"].search([("packaging_ids", "!=", False)])

        self.assertTrue(product)

        self.product.write(
            {
                "attribute_line_ids": [
                    (
                        0,
                        0,
                        {
                            "attribute_id": self.attribute_color.id,
                            "value_ids": [
                                (
                                    6,
                                    0,
                                    [
                                        self.attribute_color_red.id,
                                        self.attribute_color_blue.id,
                                    ],
                                )
                            ],
                        },
                    ),
                ]
            }
        )
        # The search on packagings should not return the product as it has several
        # variants
        product = self.env["product.template"].search([("packaging_ids", "!=", False)])

        self.assertFalse(product)

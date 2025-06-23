# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestBarcodeRequired(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.dummy_package_type = cls.env["stock.package.type"].create(
            {"name": "Dummy Package Type"}
        )
        cls.env["res.config.settings"].create(
            {"product_barcode_required": True}
        ).execute()

        # Create an attribute to allow for multiple variants
        cls.attribute_color = cls.env["product.attribute"].create(
            {
                "name": "Color",
                "sequence": 1,
            }
        )
        cls.attribute_value_red = cls.env["product.attribute.value"].create(
            {
                "name": "Red",
                "attribute_id": cls.attribute_color.id,
                "sequence": 1,
            }
        )
        cls.attribute_value_blue = cls.env["product.attribute.value"].create(
            {
                "name": "Blue",
                "attribute_id": cls.attribute_color.id,
                "sequence": 2,
            }
        )

    def test_00_create_product_product_missing_barcode(self):
        with self.assertRaises(ValidationError), self.env.cr.savepoint():
            self.env["product.product"].create(
                {
                    "name": "Unittest missing barcode",
                    "uom_id": self.env.ref("uom.product_uom_unit").id,
                    "type": "product",
                    "weight": 6.0,
                    "package_type_id": self.dummy_package_type.id,
                }
            )

    def test_01_write_product_product_missing_barcode(self):
        product = self.env["product.product"].create(
            {
                "name": "Unittest missing barcode on write",
                "uom_id": self.env.ref("uom.product_uom_unit").id,
                "type": "product",
                "weight": 6.0,
                "barcode": "1234567892",
                "package_type_id": self.dummy_package_type.id,
            }
        )

        with self.assertRaises(ValidationError), self.env.cr.savepoint():
            product.write({"barcode": ""})

    def test_02_write_product_product_missing_no_barcode_authorized(self):
        product = self.env["product.product"].create(
            {
                "name": "Unittest missing no barcode authorized on write",
                "uom_id": self.env.ref("uom.product_uom_unit").id,
                "type": "product",
                "weight": 6.0,
                "no_barcode_authorized": True,
                "package_type_id": self.dummy_package_type.id,
            }
        )

        with self.assertRaises(ValidationError), self.env.cr.savepoint():
            product.write({"no_barcode_authorized": False})

    def test_03_create_product_template_missing_barcode(self):
        with self.assertRaises(ValidationError), self.env.cr.savepoint():
            self.env["product.template"].create(
                {
                    "name": "Unittest template missing barcode",
                    "uom_id": self.env.ref("uom.product_uom_unit").id,
                    "type": "product",
                    "weight": 6.0,
                    "package_type_id": self.dummy_package_type.id,
                }
            )

    def test_04_write_product_template_missing_barcode(self):
        template = self.env["product.template"].create(
            {
                "name": "Unittest template missing barcode on write",
                "uom_id": self.env.ref("uom.product_uom_unit").id,
                "type": "product",
                "weight": 6.0,
                "barcode": "1234567892",
                "package_type_id": self.dummy_package_type.id,
            }
        )
        with self.assertRaises(ValidationError), self.env.cr.savepoint():
            template.write({"barcode": ""})

    def test_05_write_product_template_new(self):
        package_type_new = self.env["stock.package.type"].create(
            {
                "name": "Box test",
                "is_new": True,
            }
        )
        template = self.env["product.template"].create(
            {
                "package_type_id": package_type_new.id,
                "name": "Unittest template missing no barcode authorized on write",
                "uom_id": self.env.ref("uom.product_uom_unit").id,
                "type": "product",
                "weight": 6.0,
            }
        )
        self.assertFalse(template.no_barcode_authorized)

    # def test_copy_product(self):
    #     product = self.env["product.product"].create(
    #         {
    #             "name": "Unittest missing barcode on write",
    #             "uom_id": self.env.ref("uom.product_uom_unit").id,
    #             "type": "product",
    #             "weight": 6.0,
    #             "barcode": "1234567892",
    #             "no_barcode_authorized": True,
    #         }
    #     )
    #     p2 = product.copy()
    #     self.assertTrue(p2)

    def test_06_copy_template(self):
        product = self.env["product.product"].create(
            {
                "name": "Unittest missing barcode on write",
                "uom_id": self.env.ref("uom.product_uom_unit").id,
                "type": "product",
                "weight": 6.0,
                "barcode": "1234567892",
                "no_barcode_authorized": True,
            }
        )
        product_tmpl = product.product_tmpl_id
        p2 = product_tmpl.copy()
        self.assertTrue(p2)

    def test_07_update_no_barcode_authorized(self):
        product = self.env["product.product"].create(
            {
                "name": "Unittest missing barcode on write",
                "uom_id": self.env.ref("uom.product_uom_unit").id,
                "type": "product",
                "weight": 6.0,
                "barcode": "1234567892",
                "no_barcode_authorized": True,
            }
        )
        template = product.product_tmpl_id

        self.assertTrue(template.no_barcode_authorized)

        template.no_barcode_authorized = False
        self.assertFalse(product.no_barcode_authorized)

    def test_08_create_product_product_with_barcode(self):
        # Test a 'new' product
        product = self.env["product.product"].create(
            {
                "name": "Test Product",
                "barcode": "42",
            }
        )
        self.assertTrue(product.is_new, "Product is expected to be 'new'.")
        self.assertTrue(
            product, "Product with a barcode should have been created successfully."
        )

        # Test a "not 'new'" product
        product = self.env["product.product"].create(
            {
                "name": "Test Product",
                "barcode": "43",
                "package_type_id": self.dummy_package_type.id,
            }
        )
        self.assertFalse(product.is_new, "Product is expected to be 'new'.")
        self.assertTrue(
            product,
            "Product with a barcode should have been created successfully "
            "(even if not 'new).",
        )

    def test_09_create_product_template_with_barcode(self):
        # Test a 'new' product
        template = self.env["product.template"].create(
            {
                "name": "Test Template",
                "barcode": "42",
            }
        )
        self.assertTrue(template.is_new, "template is expected to be 'new'.")
        self.assertTrue(
            template, "Template with a barcode should have been created successfully."
        )

        # Test a "not 'new'" template
        template = self.env["product.template"].create(
            {
                "name": "Test Template",
                "barcode": "43",
                "package_type_id": self.dummy_package_type.id,
            }
        )
        self.assertFalse(template.is_new, "template is expected to be 'new'.")
        self.assertTrue(
            template,
            "Template with a barcode should have been created successfully "
            "(even if not 'new).",
        )

    def test_10_write_no_barcode_authorized_multiple_variants_disabled(self):
        template = self.env["product.template"].create(
            {
                "name": "Test T-Shirt",
                "type": "product",
                "attribute_line_ids": [
                    Command.create(
                        {
                            "attribute_id": self.attribute_color.id,
                            "value_ids": [
                                Command.set(
                                    [
                                        self.attribute_value_red.id,
                                        self.attribute_value_blue.id,
                                    ]
                                )
                            ],
                        }
                    )
                ],
            }
        )

        self.assertEqual(
            template.product_variant_count,
            2,
            "Expected 2 variants for the test product.",
        )
        product_variants = template.product_variant_ids
        with self.assertRaises(ValidationError):
            product_variants[0].no_barcode_authorized = (
                not template.no_barcode_authorized
            )

    def test_11_write_no_barcode_authorized_single_variant(self):
        template = self.env["product.template"].create(
            {
                "name": "Test T-Shirt",
                "type": "product",
            }
        )
        product_variant = template.product_variant_id
        product_variant.no_barcode_authorized = not template.no_barcode_authorized
        self.assertEqual(
            product_variant.no_barcode_authorized,
            template.no_barcode_authorized,
            "Updating 'no_barcode_authorized' on the variant should also update the template",
        )

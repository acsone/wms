# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestBarcodeRequired(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.dummy_storage_type = cls.env["stock.package.type"].create({"name": "dummy"})
        cls.env["res.config.settings"].create(
            {"product_barcode_required": True}
        ).execute()

    def test_00_create_product_product_missing_barcode(self):
        with self.assertRaises(ValidationError), self.env.cr.savepoint():
            self.env["product.product"].create(
                {
                    "name": "Unittest missing barcode",
                    "uom_id": self.env.ref("uom.product_uom_unit").id,
                    "type": "product",
                    "weight": 6.0,
                    "package_type_id": self.dummy_storage_type.id,
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
                "package_type_id": self.dummy_storage_type.id,
            }
        )

        with self.assertRaises(ValidationError), self.env.cr.savepoint():
            product.write({"barcode": ""})

        self.env["res.config.settings"].create(
            {"product_barcode_required": False}
        ).execute()
        product.write({"barcode": ""})

    def test_02_write_product_product_missing_no_barcode_authorized(self):
        product = self.env["product.product"].create(
            {
                "name": "Unittest missing no barcode authorized on write",
                "uom_id": self.env.ref("uom.product_uom_unit").id,
                "type": "product",
                "weight": 6.0,
                "no_barcode_authorized": True,
                "package_type_id": self.dummy_storage_type.id,
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
                    "package_type_id": self.dummy_storage_type.id,
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
                "package_type_id": self.dummy_storage_type.id,
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

    def test_copy_template(self):
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

    def test_update_no_barcode_authorized(self):
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

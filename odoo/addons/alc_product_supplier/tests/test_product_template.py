# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.tests.common import TransactionCase


class TestProductTemplate(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product_tmpl_model = cls.env["product.template"]
        cls.sinfo_model = cls.env["product.supplierinfo"]
        cls.supplier = cls.env["res.partner"].create({"name": "supplier"})
        cls.product_no_seller = cls.product_tmpl_model.create({"name": "no seller"})
        cls.product_seller = cls.product_tmpl_model.create(
            {"name": "with seller", "default_code": "1234"}
        )
        cls.supplierinfo = cls.sinfo_model.create(
            {
                "partner_id": cls.supplier.id,
                "product_code": "ABCD",
                "product_tmpl_id": cls.product_seller.id,
            }
        )

    def test_00(self):
        """
        Data:

            A product without supplier
            A supplier info with product_code "ABCD"
        Test Case:
            Link the supplier info to the product
        Expected result:
            The field vendor_product_code must be set on the product template
            The field supplier_id must be set to supplier
        """
        self.assertFalse(self.product_no_seller.vendor_product_code)
        self.assertFalse(self.product_no_seller.supplier_id)
        self.supplierinfo.product_tmpl_id = self.product_no_seller
        self.assertEqual(self.product_no_seller.vendor_product_code, "ABCD")
        self.assertEqual(self.product_no_seller.supplier_id, self.supplier)

    def test_01(self):
        """
        Data:

            A product with a seller with product_code "ABCD"
        Test Case:
            Update the product_code on the supplier info
        Expected result:
            The field vendor_product_code must be updated on the product template
        """
        self.assertEqual(self.product_seller.vendor_product_code, "ABCD")
        self.supplierinfo.product_code = "BCD"
        self.assertEqual(self.product_seller.vendor_product_code, "BCD")

    def test_03(self):
        """
        Data:

            A product with a seller with product_code "ABCD"
        Test Case:
            Replace existing seller_ids by a new supplier with an other product_code "BCD"
        Expected result:
            The field vendor_product_code must become "BCD"
        """
        self.assertEqual(self.product_seller.vendor_product_code, "ABCD")
        new_supplier = self.supplier.copy()
        self.product_seller.write(
            {
                "seller_ids": [
                    Command.clear(),
                    Command.create(
                        {
                            "product_tmpl_id": self.product_seller.id,
                            "product_code": "BCD",
                            "partner_id": new_supplier.id,
                        },
                    ),
                ]
            }
        )
        self.assertEqual(self.product_seller.supplier_id, new_supplier)
        self.assertEqual(self.product_seller.vendor_product_code, "BCD")

    def test_name_search(self):
        """Test search by vendor code."""
        self.assertEqual(
            self.env["product.product"]
            .with_context(partner_id=self.supplier.id)
            .name_search("ABCD"),
            [(self.product_seller.product_variant_ids.id, "[ABCD] with seller")],
        )

    def test_name_search_vendor_product_code(self):
        """Test search by vendor code without context."""
        self.assertEqual(
            self.env["product.product"].name_search("ABCD"),
            [(self.product_seller.product_variant_ids.id, "[1234] with seller")],
        )

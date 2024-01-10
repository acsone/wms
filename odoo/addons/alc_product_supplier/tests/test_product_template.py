# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import Command

from .common import TestProductTemplateCommon


class TestProductTemplate(TestProductTemplateCommon):
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

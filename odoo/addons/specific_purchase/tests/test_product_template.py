# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import common


class TestProductTemplate(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestProductTemplate, cls).setUpClass()
        cls.ProducTemplate = cls.env["product.template"]
        cls.ProductSupplierInfo = cls.env["product.supplierinfo"]
        cls.supplier = cls.env["res.partner"].create({"name": "supplier"})
        cls.product_no_seller = cls.ProducTemplate.create({"name": "no seller"})

        cls.supplierinfo = cls.ProductSupplierInfo.create(
            {"name": cls.supplier.id, "product_code": "ABCD"}
        )

        cls.product_seller = cls.ProducTemplate.create(
            {"name": "with seller", "seller_ids": [(6, 0, [cls.supplierinfo.id])]}
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
                    (5,),
                    (
                        0,
                        0,
                        {
                            "product_tmpl_id": self.product_seller.id,
                            "product_code": "BCD",
                            "name": new_supplier.id,
                        },
                    ),
                ]
            }
        )
        self.assertEqual(self.product_seller.supplier_id, new_supplier)
        self.assertEqual(self.product_seller.vendor_product_code, "BCD")

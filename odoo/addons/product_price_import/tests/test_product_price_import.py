# -*- coding: utf-8 -*-
# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import base64
from datetime import datetime, timedelta

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests import SavepointCase

from odoo.addons.product_price_import.wizards.product_price_importer import (
    ProductPriceInfo,
)


class TestProductPriceImport(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestProductPriceImport, cls).setUpClass()
        cls.BaseImport = cls.env["base_import.import"]
        cls.pastday = fields.Date.to_string(datetime.now() - timedelta(days=10))
        cls.yesterday = fields.Date.to_string(datetime.now() - timedelta(days=1))
        cls.tomorrow = fields.Date.to_string(datetime.now() + timedelta(days=1))
        cls.report_action = cls.env.ref(
            "product_price_import.report_product_price_import_xlsx"
        )
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.supplier = cls.env.ref("base.res_partner_12")
        cls.product = cls.env["product.product"].create(
            {
                "name": "Product 1",
                "list_price": 11.0,
                "indicated_price": 13.75,
                "default_code": "P01",
            }
        )

        cls.supplierinfo = cls.env["product.supplierinfo"].create(
            {"name": cls.supplier.id, "price": 10, "product_code": "SUP01"}
        )
        cls.supplierinfo_promo_active = cls.env["product.supplierinfo"].create(
            {
                "name": cls.supplier.id,
                "price": 10,
                "product_code": "SUP01",
                "discount_purchase": 10,
                "date_start": cls.yesterday,
                "date_end": cls.tomorrow,
            }
        )
        cls.supplierinfo_promo_future = cls.env["product.supplierinfo"].create(
            {
                "name": cls.supplier.id,
                "price": 10,
                "min_qty": 20,
                "product_code": "SUP01",
                "discount_purchase": 20,
                "date_start": cls.tomorrow,
                "date_end": cls.tomorrow,
            }
        )
        cls.supplierinfo_promo_obsolete = cls.env["product.supplierinfo"].create(
            {
                "name": cls.supplier.id,
                "price": 10,
                "min_qty": 20,
                "product_code": "SUP01",
                "discount_purchase": 20,
                "date_start": cls.pastday,
                "date_end": cls.pastday,
            }
        )
        cls.product.write({"seller_ids": [(6, 0, cls.supplierinfo.ids)]})

        cls.pricelist_pb2 = cls.env.ref("specific_data.product_pricelist_pb2")
        cls.product_pricelist_item = cls.env["product.pricelist.item"].create(
            {
                "applied_on": "1_product",
                "product_id": cls.product.id,
                "compute_price": "fixed",
                "fixed_price": 12.24,
                "product_tmpl_id": cls.product.product_tmpl_id.id,
                "pricelist_id": cls.pricelist_pb2.id,
            }
        )

        cls.generated_import_content, _ext = cls.report_action.render_report(
            cls.product.product_tmpl_id.id, cls.report_action.report_name, {}
        )
        cls.ProductPriceImporter = cls.env["product.price.importer"]
        cls.default_product_prive_info = ProductPriceInfo(
            product_id=cls._get_xml_id(cls.product.product_tmpl_id),
            supplier_id=cls._get_xml_id(cls.supplier),
            purchase_price="10.5",
            sale_price="11.5",
            sale_price_2="13.0",
            indicated_price="13.24",
            supplier_reference="NEWSUP01",
        )

    @classmethod
    def _add_promos(cls):
        cls.product.write(
            {
                "seller_ids": [
                    (4, cls.supplierinfo_promo_active.id),
                    (4, cls.supplierinfo_promo_obsolete.id),
                    (4, cls.supplierinfo_promo_future.id),
                ]
            }
        )

    @classmethod
    def _get_xml_id(cls, model):
        IrModelData = cls.env["ir.model.data"].sudo()
        data = IrModelData.search(
            [("model", "=", model._name), ("res_id", "=", model.id)]
        )
        if data:
            if data[0].module:
                return "{}.{}".format(data[0].module, data[0].name)
            else:
                return data[0].name

    def test_0(self):
        """
        Data:
            A generated import report
        Test case:
            Import the generated report
        Expected result:
            No error occurs

        Dummy test to validate the import process (not the content)
        """
        importer = self.ProductPriceImporter.create(
            {"document": base64.b64encode(self.generated_import_content)}
        )
        res = importer.doit()
        self.assertTrue(res)

    def test_1(self):
        """
        Data:
            ProductPriceInfo with wrong product xml_id
        Test Case:
            call the price update logic _do_update_prices
        Expected result:
            ValidationError is raised
        """
        price_info = self.default_product_prive_info.copy()
        self.ProductPriceImporter._do_update_prices([price_info])
        price_info.product_id = "wrong"
        with self.assertRaises(ValidationError), self.env.cr.savepoint():
            self.ProductPriceImporter._do_update_prices([price_info])
        price_info.product_id = None
        with self.assertRaises(ValidationError), self.env.cr.savepoint():
            self.ProductPriceImporter._do_update_prices([price_info])

    def test_2(self):
        """
        Data:
            ProductPriceInfo with wrong supplier xml_id
        Test Case:
            call the price update logic _do_update_prices
        Expected result:
            ValidationError is raised
        """
        price_info = self.default_product_prive_info.copy()
        self.ProductPriceImporter._do_update_prices([price_info])
        price_info.supplier_id = "wrong"
        with self.assertRaises(ValidationError), self.env.cr.savepoint():
            self.ProductPriceImporter._do_update_prices([price_info])
        price_info.supplier_id = None
        with self.assertRaises(ValidationError), self.env.cr.savepoint():
            self.ProductPriceImporter._do_update_prices([price_info])

    def test_3(self):
        """
        Data:
            A product with a supplier and all the prices filled
            ProductPriceInfo with new values for all the fields price
        Test Case:
            call the price update logic _do_update_prices
        Expected result:
            Price fields on the product are updated
        """
        price_info = self.default_product_prive_info.copy()
        self.assertNotEqual(float(price_info.sale_price), self.product.list_price)
        self.assertNotEqual(
            float(price_info.indicated_price), self.product.indicated_price
        )
        self.assertNotEqual(float(price_info.sale_price_2), self.product.sale_price_2)
        self.assertNotEqual(
            float(price_info.purchase_price), self.product.seller_ids[0].price
        )
        self.ProductPriceImporter._do_update_prices([price_info])
        self.product.refresh()
        self.assertEqual(float(price_info.sale_price), self.product.list_price)
        self.assertEqual(
            float(price_info.indicated_price), self.product.indicated_price
        )
        self.assertEqual(float(price_info.sale_price_2), self.product.sale_price_2)
        self.assertEqual(
            float(price_info.purchase_price), self.product.seller_ids[0].price
        )

    def test_4(self):
        """
        Data:
            A product without supplier
            ProductPriceInfo with new values for all the fields price
        Test Case:
            call the price update logic _do_update_prices
        Expected result:
            A new default supplier is created with the supplier_reference and
            the given price
        """
        price_info = self.default_product_prive_info.copy()
        self.product.seller_ids.unlink()
        self.assertFalse(self.product.seller_ids)
        self.ProductPriceImporter._do_update_prices([price_info])
        self.product.refresh()
        self.assertEqual(
            float(price_info.purchase_price), self.product.seller_ids[0].price
        )
        self.assertEqual(
            price_info.supplier_reference, self.product.seller_ids[0].product_code
        )
        self.assertEqual(
            price_info.supplier_reference, self.product.vendor_product_code
        )

    def test_5(self):
        """
        Data:
            A product with a supplier and all the prices filled
            ProductPriceInfo with sale_price_2 == "0"
        Test Case:
            call the price update logic _do_update_prices
        Expected result:
            sale_price_2 becomes None
            related pricelistitem is removed
        """
        price_info = self.default_product_prive_info.copy()
        self.product.refresh()
        self.assertTrue(self.product.sale_price_2)
        price_info.sale_price_2 = "0"
        self.ProductPriceImporter._do_update_prices([price_info])
        self.product.refresh()
        self.assertFalse(self.product.sale_price_2)
        self.assertFalse(self.product_pricelist_item.exists())

    def test_6(self):
        """
        Data:
            A product with a supplier and all the prices filled
            ProductPriceInfo with sale_price_2 == ""
        Test Case:
            call the price update logic _do_update_prices
        Expected result:
            sale_price_2 becomes None
            related pricelistitem is removed
        """
        price_info = self.default_product_prive_info.copy()
        self.product.refresh()
        self.assertTrue(self.product.sale_price_2)
        price_info.sale_price_2 = ""
        self.ProductPriceImporter._do_update_prices([price_info])
        self.product.refresh()
        self.assertFalse(self.product.sale_price_2)
        self.assertFalse(self.product_pricelist_item.exists())

    def test_7(self):
        """
        Data:
            A product without sale_price_2
            ProductPriceInfo with sale_price_2
        Test Case:
            call the price update logic _do_update_prices
        Expected result:
            sale_price_2 is filled
            a new pricelistitem is created for the given product
        """
        price_info = self.default_product_prive_info.copy()
        self.product_pricelist_item.unlink()
        self.product.refresh()
        self.assertFalse(self.product.sale_price_2)
        self.assertEqual(
            0,
            self.env["product.pricelist.item"].search_count(
                [("product_id", "=", self.product.id)]
            ),
        )
        self.ProductPriceImporter._do_update_prices([price_info])
        self.product.refresh()
        self.assertEqual(float(price_info.sale_price_2), self.product.sale_price_2)
        self.assertEqual(
            1,
            self.env["product.pricelist.item"].search_count(
                [("product_id", "=", self.product.id)]
            ),
        )

    def test_8(self):
        """
        Data:
            A product with supplier promos (1 active , 1 future,  1 obsolete)
        Test Case:
            call the price update logic _do_update_prices
        Expected result:
            The active promo is updated (price)
            The obsolete promo is untouched
            Thr future promo is updated (price)
        """
        self._add_promos()
        self.assertEqual(len(self.product.seller_ids), 4)
        price_info = self.default_product_prive_info.copy()
        self.assertNotEqual(
            self.supplierinfo_promo_active.price, float(price_info.purchase_price)
        )
        self.assertNotEqual(
            self.supplierinfo_promo_future.price, float(price_info.purchase_price)
        )
        self.assertNotEqual(
            self.supplierinfo_promo_obsolete.price, float(price_info.purchase_price)
        )

        self.ProductPriceImporter._do_update_prices([price_info])
        self.supplierinfo_promo_active.refresh()
        self.assertEqual(
            self.supplierinfo_promo_active.price, float(price_info.purchase_price)
        )
        self.assertEqual(
            self.supplierinfo_promo_future.price, float(price_info.purchase_price)
        )
        self.assertNotEqual(
            self.supplierinfo_promo_obsolete.price, float(price_info.purchase_price)
        )

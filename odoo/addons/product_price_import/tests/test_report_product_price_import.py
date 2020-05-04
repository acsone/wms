# -*- coding: utf-8 -*-
# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import xlrd
from odoo.tests import SavepointCase


class TestReportProductPriceImport(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestReportProductPriceImport, cls).setUpClass()
        cls.BaseImport = cls.env["base_import.import"]
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
        cls.product.write({"seller_ids": [(6, 0, cls.supplierinfo.ids)]})

        cls.pricelist_pb2 = cls.env.ref("specific_data.product_pricelist_pb2")
        cls.pricelist_pb2.item_ids = [
            (
                0,
                False,
                {
                    "applied_on": "1_product",
                    "product_id": cls.product.id,
                    "compute_price": "fixed",
                    "fixed_price": 12.24,
                    "product_tmpl_id": cls.product.product_tmpl_id.id,
                },
            )
        ]

    def _get_xml_id(self, model):
        IrModelData = self.env["ir.model.data"].sudo()
        data = IrModelData.search(
            [("model", "=", model._name), ("res_id", "=", model.id)]
        )
        if data:
            if data[0].module:
                return "%s.%s" % (data[0].module, data[0].name)
            else:
                return data[0].name

    def test_0(self):
        """
        Data:
            A product with a supplier and all the prices filled
        Test case:
            Generate the report
        Expected result:
            A binary content with an xslx extension

        Dummy test to validate the generation process (not the content)
        """
        content, ext = self.report_action.render_report(
            self.product.product_tmpl_id.id, self.report_action.report_name, {}
        )
        self.assertIsNotNone(content)
        self.assertEqual(ext, "xlsx")

    def test_1(self):
        """
        Data:
            A product with a supplier and all the prices filled
        Test case:
            Generate the report
        Expected result:
            A xsl file with  1 worksheet is created
            The first worksheet contains 2 lines
            The first line is the header line with values:
             * product_id
             * supplier_id
             * supplier_name
             * product_name
             * internal_reference,
             * supplier_reference
             * purchase_price
             * sale_price
             * sale_price_2
             * indicated_price
            The second line contains the values for the given product.
        """
        content, ext = self.report_action.render_report(
            self.product.product_tmpl_id.id, self.report_action.report_name, {}
        )
        book = xlrd.open_workbook(file_contents=content)
        rows = [r for r in self.BaseImport._read_xls_book(book)]
        headers = rows[0]
        self.assertListEqual(
            headers,
            [
                "product_id",
                "supplier_id",
                "supplier_name",
                "product_name",
                "internal_reference",
                "supplier_reference",
                "sale_taxes",
                "purchase_price",
                "sale_price",
                "sale_price_2",
                "indicated_price",
            ],
        )
        values = rows[1]
        self.assertListEqual(
            values,
            [
                self._get_xml_id(self.product.product_tmpl_id),
                self._get_xml_id(self.supplier),
                self.supplier.name,
                u"Product 1",
                u"P01",
                u"SUP01",
                ", ".join(self.product.mapped("taxes_id.name")),
                u"10",
                u"11",
                u"12.24",
                u"13.75",
            ],
        )

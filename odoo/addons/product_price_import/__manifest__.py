# -*- coding: utf-8 -*-
# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Product Price Import",
    "summary": "Product prices mass import",
    "description": """
Product prices mass import
--------------------------

This addon provides:

* A new report with the current prices by product into xls format
* A new wizard to import the generated report and apply changes to
  the different prices defined for a product (purchase, sale 1 , sale 2
  and indicated)
        """,
    "version": "10.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        "pricelist_discount",
        "specific_product",
        "specific_purchase",
        "report_xlsx_helper",
        "base_import",
    ],
    "data": [
        "wizards/product_price_importer.xml",
        "report/report_product_price_import.xml",
    ],
    "demo": [],
}

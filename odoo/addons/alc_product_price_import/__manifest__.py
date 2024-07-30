# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Product Price Import",
    "summary": "Alcyon: Product prices mass import",
    "description": """
Product prices mass import
--------------------------

This addon provides:

* A new report with the current prices by product into xls format
* A new wizard to import the generated report and apply changes to
  the different prices defined for a product (purchase, sale 1 , sale 2
  and indicated)
        """,
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # Custom
        "alc_product_additional_price",
        "alc_product_pricelist_data",
        # OCA
        "report_xlsx_helper",
        # Others
        "base_import",
        "purchase",
    ],
    "data": [
        "security/ir.model.access.csv",
        "wizards/alc_product_price_importer_views.xml",
        "report/report_product_price_import.xml",
    ],
    "demo": [],
    "external_dependencies": {"python": ["xlrd<2"]},
    "installable": True,
}

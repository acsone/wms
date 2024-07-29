# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Product Consolidated Price Report",
    "description": """
        Alcyon: Partner Consolidated Price CSV report""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # fmt: off
        # Custom
        "alc_product_flattened_data",
        # OCA
        "report_csv",
        # fmt: on
    ],
    "data": ["reports/alc_product_consolidated_price_csv_report.xml"],
    "demo": [],
    "installable": True,
}

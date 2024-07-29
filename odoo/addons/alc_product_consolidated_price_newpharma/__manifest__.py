# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Product Consolidated Price Newpharma",
    "description": """
        Alcyon: controller to expose consolidated prices for NewPharma""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # fmt: off
        # Custom
        "alc_product_consolidated_price_report",
        "alc_product_newpharma",
        # fmt: on
    ],
    "data": [],
    "demo": [],
    "installable": True,
}

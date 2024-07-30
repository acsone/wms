# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc App Packaging",
    "description": """
        A temporary app to install addons to use to manage packaging on products""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://www.acsone.eu",
    "depends": [
        # OCA
        "product_supplierinfo_packaging",
        "purchase_only_by_packaging",
        "purchase_stock_packaging",
    ],
    "data": [],
    "demo": [],
    "installable": True,
    "application": True,
    "development_status": "Alpha",
}

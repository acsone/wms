# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Eshop Sale Product Unavailable",
    "description": """
        Alcyon: Add unavailable qty on order line info""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # fmt: off
        # Custom
        "alc_sale_product_qty_unavailable",
        # OCA
        "shopinvader_schema_sale",
        # fmt: on
    ],
    "data": [],
    "demo": [],
    "installable": True,
    "development_status": "Alpha",
}

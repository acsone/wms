# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Pricelist Items",
    "description": """
        List pricelist items in a new screen""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "depends": [
        # OCA
        "product_price_category",
        # Others
        "product",
    ],
    "data": ["views/product_pricelist.xml"],
    "demo": [],
}

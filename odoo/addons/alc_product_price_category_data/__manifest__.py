# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Product Price Category Data",
    "description": """
        This addon define base data for product price category""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        # OCA
        "product_price_category",
    ],
    "data": ["data/product_price_category.xml"],
    "pre_init_hook": "pre_init_hook",
}

# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Product Category Data",
    "description": """
        This addon define base data for product category""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        # fmt: off
        # Custom
        "alc_product_category_business_unit",
        "alc_product_food",
        # Others
        "stock_account",
        # fmt: on
    ],
    "data": ["data/product_category.xml"],
    "pre_init_hook": "pre_init_hook",
}

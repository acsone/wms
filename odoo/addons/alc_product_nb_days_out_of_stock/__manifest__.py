# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Product Nb Days Out Of Stock",
    "description": """
        This addon a filed to product template to highlight the Number of days before
         running out of stock""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        # Custom
        "alc_product_average_sale",
        # Others
        "sale_stock",
    ],
    "data": ["views/product_template.xml"],
    "demo": [],
}

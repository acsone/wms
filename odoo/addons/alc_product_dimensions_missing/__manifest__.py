# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Product Dimensions Missing",
    "description": """
        Show whether products and product packages are missing dimensions""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        # fmt: off
        # Custom
        "alc_product_template_packaging_search",
        # OCA
        "product_dimension",
        "product_packaging_dimension",
        # fmt: on
    ],
    "data": [
        "views/product_template.xml",
    ],
    "demo": [],
}

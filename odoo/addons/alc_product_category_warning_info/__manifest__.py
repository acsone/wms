# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Product Category Warning Info",
    "description": """
        Allows to define a warning information for customers on product category level""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        # fmt: off
        # Others
        "product",
        # fmt: on
    ],
    "data": [
        "views/product_category.xml",
    ],
}

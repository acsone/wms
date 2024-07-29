# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Product Incoming Stock Move Action",
    "description": """This addon add an action to the product form view to display
    related incoming moves""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        # fmt: off
        # Others
        "stock",
        # fmt: on
    ],
    "data": ["views/product_product.xml", "views/product_template.xml"],
    "demo": [],
}

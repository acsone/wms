# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Product Supplierinfo Force Edit Form",
    "description": """
        Alcyon: Force the use of edit form to add or modify a supplierinfo line into the product view""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # fmt: off
        # Others
        "purchase",
        # fmt: on
    ],
    "data": ["views/product_supplierinfo.xml"],
    "demo": [],
}

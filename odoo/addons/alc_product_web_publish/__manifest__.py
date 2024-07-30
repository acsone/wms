# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Product Web Publish",
    "description": """this addon adds a field to track products published on the website
    """,
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        # Others
        "product",
    ],
    "data": ["views/product_template.xml"],
    "pre_init_hook": "pre_init_hook",
}

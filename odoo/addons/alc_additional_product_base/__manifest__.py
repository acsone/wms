# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Additional Product Base",
    "description": """
        This addon define additional product that can be used in purchase and sale""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        # Others
        "product",
    ],
    "data": ["views/product_template.xml"],
    "demo": [],
    "pre_init_hook": "pre_init_hook",
}

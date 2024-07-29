# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Additional Product Purchase",
    "description": """
        This addon define additional product in purchase flow""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "category": "Product",
    "depends": [
        # fmt: off
        # Custom
        "alc_additional_product_base",
        # Others
        "purchase",
        # fmt: on
    ],
    "data": ["views/purchase_order.xml"],
    "installable": True,
    "pre_init_hook": "pre_init_hook",
}

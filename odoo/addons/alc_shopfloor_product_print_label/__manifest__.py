# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Shopfloor Product Print Label",
    "description": """
        allow to print product labels from shopfloor""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "depends": [
        # fmt: off
        # Custom
        "alc_product_label_printer",
        "alc_product_label_printing",
        # OCA
        "shopfloor",
        # fmt: on
    ],
    "data": ["views/shopfloor_menu.xml"],
    "demo": [],
}

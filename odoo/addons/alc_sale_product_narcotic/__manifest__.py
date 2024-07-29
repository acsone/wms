# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Sale Product Narcotic",
    "description": """
        Add a warning to notify the user that a voucher is required to buy narcotics""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        # fmt: off
        # Custom
        "alc_product_pharmacy",
        # Others
        "sale",
        # fmt: on
    ],
    "data": ["views/product.xml"],
    "demo": [],
}

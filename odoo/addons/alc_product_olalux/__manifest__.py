# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Product Olalux",
    "description": """
        Define a domain for products available to Olalux to be used with webservices""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        # fmt: off
        # Custom
        "alc_product_category_data",
        "alc_product_food",
        # OCA
        "partner_manual_rank",
        # fmt: on
    ],
}

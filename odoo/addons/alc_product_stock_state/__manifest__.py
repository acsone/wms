# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Product Stock State",
    "description": """
        Alcyon: Add new state when product is temporarily not available at supplier level""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # Custom
        "alc_product_state",
        # OCA
        "product_stock_state",
        "stock_available",
    ],
    "data": [],
    "demo": [],
}

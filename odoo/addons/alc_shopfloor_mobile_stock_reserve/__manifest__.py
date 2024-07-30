# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Shopfloor Mobile Stock Reserve",
    "description": """
        frontend logic for reserve management in shopfloor specific to alcyon""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "depends": [
        # Custom
        "alc_shopfloor_stock_reserve",
        # OCA
        "shopfloor_mobile",
    ],
    "data": ["templates/assets.xml"],
    "demo": [],
}

# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Shopfloor Product Info",
    "description": """
        This addon adds a flag to the stock location model to indicate which internal
        location we want to display in the product information within the shopfloor
        application.""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        # fmt: off
        # OCA
        "shopfloor",
        # fmt: on
    ],
    "data": ["views/stock_location.xml"],
    "pre_init_hook": "pre_init_hook",
}

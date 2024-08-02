# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Stock Lot Is Empty",
    "description": """
        This addon introduces a computed field, is_empty, to the stock lot model. This enhancement enables users to efficiently search for and identify empty stock lots.""",
    "version": "16.0.1.0.1",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        # Others
        "stock",
    ],
    "data": ["views/stock_lot.xml"],
    "pre_init_hook": "pre_init_hook",
}

# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Stock Valuation Layer Operation Type",
    "description": """
        operation type on stock valuation layer""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        # Others
        "stock_account",
    ],
    "data": ["views/stock_valuation_layer.xml"],
    "pre_init_hook": "pre_init_hook",
}

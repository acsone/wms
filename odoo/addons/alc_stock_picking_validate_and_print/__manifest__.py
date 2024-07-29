# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Stock Picking Validate And Print",
    "description": """
        This addon adds an action to pickings to allow validation and print in one step""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        # fmt: off
        # Others
        "stock",
        # fmt: on
    ],
    "data": [
        "views/stock_picking.xml",
    ],
    "demo": [],
}

# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Stock Refill View",
    "description": """
        Alcyon: Add menu and specific views to display pending refills""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        "alc_stock_move_line_current_release_channel",
        "alc_stock_move_line_priority",
        "stock",
    ],
    "data": [
        "views/stock_move_line.xml",
    ],
    "pre_init_hook": "pre_init_hook",
}

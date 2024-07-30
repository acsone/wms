# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Stock Picking Type Aliment",
    "description": """
        Allows to define the picking type Aliments""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        # OCA
        "stock_picking_completion_info",
        # Others
        "stock",
    ],
    "data": [
        "data/stock_picking_type.xml",
    ],
    "pre_init_hook": "pre_init_hook",
}

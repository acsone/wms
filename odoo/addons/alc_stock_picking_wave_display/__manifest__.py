# -*- coding: utf-8 -*-
# Copyright 2022 ACOSNE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Stock Picking Wave Display",
    "description": """
        Display wave_id avec wave_state on stock picking tree view""",
    "version": "10.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACOSNE SA/NV",
    "depends": [
        # TODO: has been removed "specific_zetes",
        "stock_picking_wave"
    ],
    "data": ["views/stock_picking.xml"],
    'installable': False
}
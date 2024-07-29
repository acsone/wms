# Copyright 2023 ACSONE SA/NV
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

{
    "name": "Alc Stock Picking Backorder Reason",
    "description": """
        Defines data for Alcyon when managing backorder reasons""",
    "version": "16.0.1.0.0",
    "license": "LGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        # fmt: off
        # OCA
        "stock_picking_backorder_reason",
        # fmt: on
    ],
    "data": [
        "data/stock_backorder_reason.xml",
    ],
}

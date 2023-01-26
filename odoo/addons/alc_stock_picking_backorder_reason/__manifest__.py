# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Stock Picking Backorder Reason",
    "description": """
        Allows to define specific flows for Alcyon when managing backorder reasons""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": ["stock_picking_backorder_reason", "stock_picking_backorder_reason_grn"],
    "data": [
        "data/stock_backorder_reason.xml",
    ],
}

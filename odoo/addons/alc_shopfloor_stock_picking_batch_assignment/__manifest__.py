# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Shopfloor Stock Picking Batch Assignment",
    "description": """Show an error message if user is already assigned to a batch""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        # fmt: off
        # Custom
        "alc_stock_picking_batch_assignment",
        # OCA
        "shopfloor",
        "shopfloor_batch_automatic_creation",
        "stock_picking_batch_start",
        # fmt: on
    ],
    "data": [],
    "demo": [],
}

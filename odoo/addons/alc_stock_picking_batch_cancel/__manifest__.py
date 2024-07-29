# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Stock Picking Batch Cancel",
    "description": """
        This addon define the cancel action visibility for stock batches""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        # fmt: off
        # Others
        "stock_picking_batch",
        # fmt: on
    ],
    "data": ["views/stock_picking_batch.xml"],
    "demo": [],
}

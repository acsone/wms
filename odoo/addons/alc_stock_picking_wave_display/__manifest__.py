# Copyright 2022 ACOSNE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Stock Picking Wave Display",
    "description": """
        Display batch_id with batchb_state on stock picking tree view""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "depends": [
        # Others
        "stock_picking_batch",
    ],
    "data": ["views/stock_picking.xml"],
    "installable": True,
}

# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Stock Picking Cancel Permission",
    "description": """
        Add permission on users to uncancel pickings""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "depends": [
        # OCA
        "stock_picking_back2draft",
    ],
    "data": ["security/res_groups.xml", "views/stock_picking_views.xml"],
    "pre_init_hook": "pre_init_hook",
}

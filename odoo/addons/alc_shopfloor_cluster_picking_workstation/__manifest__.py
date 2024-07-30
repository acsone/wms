# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Shopfloor Cluster Picking Workstation",
    "description": """
        Add workstation screen for cluster picking""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "depends": [
        # OCA
        "shopfloor",
        "shopfloor_packing",
        "shopfloor_workstation",
    ],
    "data": ["views/shopfloor_menu.xml", "views/stock_picking_batch.xml"],
    "demo": [],
}

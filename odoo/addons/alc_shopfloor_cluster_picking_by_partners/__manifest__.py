# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Shopfloor Cluster Picking By Partners",
    "description": """
        allows to create cluster picking by grouping pickings by partners in bins on the trolley""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "depends": [
        # OCA
        "shopfloor_batch_automatic_creation",
        "shopfloor_packing",
    ],
    "data": ["views/shopfloor_menu.xml"],
    "demo": [],
}

# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Shopfloor Mobile Cluster Picking Workstation",
    "description": """add step for workstation selection""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "depends": [
        # fmt: off
        # Custom
        "alc_shopfloor_cluster_picking_workstation",
        # OCA
        "shopfloor_mobile",
        # fmt: on
    ],
    "data": ["templates/assets.xml"],
    "demo": [],
}

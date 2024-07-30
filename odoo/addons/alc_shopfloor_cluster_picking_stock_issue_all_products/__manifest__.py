# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Shopfloor Cluster Picking Stock Issue All Products",
    "description": """Release the batch if all products are in stock issue state""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "depends": [
        # Custom
        "alc_shopfloor_cluster_picking_workstation",
        "alc_shopfloor_loss_quantity",
        # OCA
        "shopfloor",
    ],
}

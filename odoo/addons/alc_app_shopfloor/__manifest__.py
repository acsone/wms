# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc App Shopfloor",
    "description": """
        Gather all shopfloor related modules for Alcyon""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        # OCA
        "shopfloor",
        "shopfloor_workstation",
        "shopfloor_workstation_mobile",
        "shopfloor_mobile",
        "shopfloor_mobile_base_auth_api_key",
        "shopfloor_batch_automatic_creation",
        "shopfloor_rest_log",
        "shopfloor_packing",
        # ALC
        "alc_shopfloor_stock_release_channel",
        "alc_shopfloor_mobile_cluster_picking",
        "alc_shopfloor_mobile_cluster_picking",
        "alc_shopfloor_mobile_cluster_picking_informations",
    ],
    "data": [],
    "demo": [],
}

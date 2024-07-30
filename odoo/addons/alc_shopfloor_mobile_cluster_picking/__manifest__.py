# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Shopfloor Mobile Cluster Picking",
    "description": """
        Alcyon: Add specific info on cluster picking screens""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # Custom
        "alc_shopfloor_stock_release_channel",
        "alc_stock_release_channel_code",
        "alc_stock_release_channel_picking_batch_creation",
        # OCA
        "shopfloor_batch_automatic_creation",
        "shopfloor_mobile",
    ],
    "data": ["templates/assets.xml"],
    "demo": [],
}

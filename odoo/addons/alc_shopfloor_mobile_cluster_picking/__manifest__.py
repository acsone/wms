# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Shopfloor Mobile Cluster Picking",
    "description": """
        Alcyon: Add specific info on cluster picking screens""",
    "version": "10.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        "alc_shopfloor_cluster_picking",
        "alc_shopfloor_delivery_rounds",
        "alc_shopfloor_mobile",
        "alc_stock_picking_batch_delivery_rounds",
    ],
    "data": ["templates/assets.xml"],
    "demo": [],
    'installable': False
}
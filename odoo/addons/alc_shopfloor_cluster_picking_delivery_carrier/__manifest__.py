# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Shopfloor Cluster Picking Delivery Carrier",
    "description": """
        Add a list of carriers to a shopfloor specific scenario to filter out the delivery rounds in the cluster""",
    "version": "10.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "depends": [
        "delivery",
        "alc_shopfloor_cluster_picking",
        "alc_stock_picking_batch_delivery_carrier",
    ],
    "data": ["views/shopfloor_menu.xml"],
}

# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Shopfloor Delivery Rounds",
    "description": """
        add delivery round on current picking""",
    "version": "10.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "depends": ["alc_shopfloor_cluster_picking", "delivery_rounds"],
    "data": ["views/shopfloor_menu.xml"],
    'installable': False
}
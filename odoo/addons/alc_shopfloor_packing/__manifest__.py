# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Shopfloor Packing",
    "description": """
        Alcyon: Manage Packing into cluster picking""",
    "version": "10.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        "alc_shopfloor",
        # has been replaced by internal_stock_quant_package "alc_internal_stock_quant_package",
    ],
    "data": ["views/shopfloor_menu.xml", "views/stock_picking.xml"],
    "demo": [],
    "pre_init_hook": "pre_init_hook",
    'installable': False
}
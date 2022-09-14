# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Shopfloor Location Content Relocation",
    "description": """
        Alcyon: Specific process to allows safe relocation of stock location by taking into account the kind of location to relocate.""",
    "version": "10.0.1.0.1",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": ["alc_shopfloor", "stock_refill"],
    "data": ["views/shopfloor_menu.xml"],
    "demo": [],
    "post_init_hook": "post_init_hook",
    'installable': False
}
# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


{
    "name": "Alcyon Discount Pricelist",
    "description": """Alcyon Discount Pricelist""",
    "version": "10.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": ["pricelist_discount"],
    "application": False,
    "data": ["views/product_pricelist.xml"],
    "demo": [],
    "installable": False,
    "pre_init_hook": "pre_init_hook",
}

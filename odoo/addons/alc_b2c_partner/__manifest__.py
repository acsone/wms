# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc B2c Partner",
    "description": """
        Alcyon: Add B2C category for patners""",
    "version": "10.0.2.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": ["alc_partner_manual_sale_order"],
    "data": [
        "data/res_partner_category.xml",
        "data/res_partner.xml",
        "views/res_partner.xml",
    ],
    "demo": [],
    "external_dependencies": {"python": ["openupgradelib"]},
    "pre_init_hook": "pre_init_hook",
    'installable': False
}
# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Veterinary Group",
    "description": """
        Alcyon: Manage veterinary groups""",
    "version": "10.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": ["product", "sales_team", "web_widget_color"],
    "data": [
        "security/veterinary_group.xml",
        "views/product_template.xml",
        "views/res_partner.xml",
        "views/veterinary_group.xml",
    ],
    "demo": [],
    "pre_init_hook": "pre_init_hook",
    'installable': False
}
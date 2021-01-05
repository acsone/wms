# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Alc Supplier Purchase Manager",
    "description": """
        ALcyon: Define puchase manager on supplier""",
    "version": "10.0.1.0.0",
    "license": "LGPL-3",  # MUST BE LGPL since will be mixed with helpdesk
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": ["base"],
    "data": ["views/res_partner.xml"],
    "demo": [],
    "external_dependencies": {"python": ["openupgradelib"]},
    "pre_init_hook": "pre_init_hook",
}

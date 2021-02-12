# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Product Mto",
    "description": """
        Alcyon: Marks products with mto route""",
    "version": "10.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": ["stock"],
    "data": ["views/product_template.xml"],
    "demo": [],
    "external_dependencies": {"python": ["openupgradelib"]},
    "pre_init_hook": "pre_init_hook",
}

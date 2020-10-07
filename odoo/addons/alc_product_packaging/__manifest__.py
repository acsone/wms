# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Product Packaging",
    "description": """
        Alcyon: Product packaging""",
    "version": "10.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": ["product_packaging_type", "product_packaging_type_pallet", "purchase"],
    "data": ["data/product_packaging_type.xml", "views/product_template.xml"],
    "demo": [],
    "external_dependencies": {"python": ["openupgradelib"]},
    "pre_init_hook": "pre_init_hook",
    "post_init_hook": "post_init_hook",
}

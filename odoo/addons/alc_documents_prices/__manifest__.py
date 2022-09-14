# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alcyon Documents Prices",
    "description": """Alcyon Documents Prices""",
    "version": "10.0.1.0.3",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": ["alc_documents", "alc_product_flattened_data"],
    "data": ["data/ir_config_parameter.xml"],
    "demo": [],
    "external_dependencies": {"python": ["unicodecsv"]},
    "post_init_hook": "post_init_hook",
    'installable': False
}
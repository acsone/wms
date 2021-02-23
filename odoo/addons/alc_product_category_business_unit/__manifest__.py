# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Product Category Business Unit",
    "description": """
        Business unit on product category""",
    "version": "10.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "depends": ["product"],
    "data": ["views/product_template.xml", "views/product_category.xml"],
    "demo": [],
    "pre_init_hook": "pre_init_hook",
}

# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Product Is New",
    "description": """
        Flag for new products in alc""",
    "version": "10.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "depends": ["alc_stock_storage_type", "product", "stock_storage_type"],
    "data": ["views/product_template.xml"],
    "external_dependencies": {"python": ["openupgradelib"]},
    "pre_init_hook": "pre_init_hook",
    'installable': False
}
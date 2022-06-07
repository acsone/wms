# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Shopinvader Url Locales",
    "description": """
        Shopinvafder: Add localized urls on products and categories""",
    "version": "10.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": ["shopinvader"],
    "data": ["data/ir_export_category.xml", "data/ir_export_product.xml"],
    "demo": [],
    "post_init_hook": "post_init_hook",
}

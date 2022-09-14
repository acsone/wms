# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Storage Media Product",
    "description": """
        Alcyon: Product media""",
    "version": "10.0.1.0.1",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        "alc_storage",
        "alc_storage_media_lang",
        "storage_media_product",
        "web_kanban",
    ],
    "data": [
        "views/js.xml",
        "views/product_media_relation.xml",
        "views/product_template.xml",
    ],
    "demo": [],
    "post_init_hook": "post_init_hook",
    'installable': False
}
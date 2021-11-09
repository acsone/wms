# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alcyon Customer Type",
    "description": """Product Category Properties""",
    "version": "10.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": ["base_cached_xmlid", "alc_product_pharmacy"],
    "application": False,
    "data": ["views/res_partner.xml"],
    "demo": [],
    "post_init_hook": "post_init_hook",
}

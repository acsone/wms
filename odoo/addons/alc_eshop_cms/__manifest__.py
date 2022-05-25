# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Eshop Cms",
    "description": """
        Alcyon: Eshop CMS""",
    "version": "10.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        "authenticated_partner_mixin",
        "base_jsonify",
        "base_rest",
        "sales_team",
        "storage_image",
    ],
    "data": [
        "data/alc_eshop_cms_snippet.xml",
        "security/res_groups.xml",
        "security/alc_eshop_cms_news.xml",
        "security/alc_eshop_cms_snippet.xml",
        "views/alc_eshop_cms_menu.xml",
        "views/alc_eshop_cms_news.xml",
        "views/alc_eshop_cms_snippet.xml",
    ],
    "external_dependencies": {"python": ["slugify"]},
    "demo": [],
}

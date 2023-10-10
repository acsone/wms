# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Eshop Ads",
    "description": """
        Alcyon: Manage ads on eshop""",
    "version": "10.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # removed        "mixin_file_id",
        # removed        "mixin_image_id",
        "mixin_past",
        "sales_team"
    ],
    "data": [
        "security/res_groups.xml",
        "security/storage_backend.xml",
        "security/storage_file.xml",
        "security/storage_image.xml",
        "security/alc_eshop_ads.xml",
        "views/alc_eshop_ads.xml",
    ],
    "demo": [],
    'installable': False
}
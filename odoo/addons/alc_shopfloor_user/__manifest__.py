# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Shopfloor User",
    "description": """
        Alcyon: Uses portal user as shopfloor user. The portal user comes from the api key""",
    "version": "10.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": ["alc_shopfloor", "auth_api_key"],
    "data": ["views/auth_api_key.xml"],
    "demo": [],
}

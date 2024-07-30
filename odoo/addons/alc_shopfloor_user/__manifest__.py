# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Shopfloor User",
    "description": """
        Alcyon: Uses portal user as shopfloor user. The portal user comes from the api key""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # OCA
        "shopfloor_base",
        "shopfloor_mobile_base_auth_api_key",
    ],
    "data": ["views/auth_api_key.xml"],
    "demo": [],
}

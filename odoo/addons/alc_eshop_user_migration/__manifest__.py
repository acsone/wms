# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Alc Eshop User Migration",
    "description": """
        REST endpoints used by 'keycloak-user-migration' to import users from
        legacy magento system.

        Provides two endpoints (GET and POST) under '/shopivader/magento_user_import/<user_name:str>'
        see https://github.com/daniel-frak/keycloak-user-migration
        """,
    "version": "10.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": ["base_rest", "shopinvader"],
    "data": [
        "security/magento_user.xml",
        "views/magento_user.xml",
        "data/ir_config_parameter.xml",
    ],
    "external_dependencies": {"python": ["apispec", "requests"]},
    'installable': False
}
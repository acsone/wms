# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alcyon E-Shop Application",
    "description": """Install all apps and modules required by the E-Shop""",
    "version": "10.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        "alc_eshop",
        "alc_search_engine",
        "alc_keycloak",
        "alc_eshop_product_promotion_subscription",
    ],
    "application": True,
    "data": [
        "security/res_groups.xml",
        "security/rule+acl_alc_product_promotion_subscription.xml",
        "security/rule+acl_product_product.xml",
        "security/rule+acl_res_partner.xml",
        "data/res_users.xml",
        "data/auth_jwt_validator.xml",
    ],
    "demo": [],
}

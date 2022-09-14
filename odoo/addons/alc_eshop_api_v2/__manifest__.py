# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Eshop Api V2",
    "description": """
        Alcyon: Add entry point for shopinvader api V2""",
    "version": "10.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        "alc_eshop_auth_jwt",
        "shopinvader_sale_cart",
        "shopinvader_sale_cart_delivery",
        "alc_eshop_sale_cart_channel",
        "alc_eshop_sale_cart_csv",
        "alc_eshop_sale_cart_confirm",
        "alc_eshop_sale_cart_payment_info",
        "alc_eshop_sale_cart_suite_name",
        "alc_eshop_sale_cart_product_unavailable",
        "alc_eshop_sale_no_cart_get",
    ],
    "data": ["views/shopinvader_menu.xml"],
    "demo": [],
    'installable': False
}
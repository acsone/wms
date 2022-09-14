# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Eshop Sale Stats",
    "description": """
        Alcyon: EShop services providing statistics on sales""",
    "version": "10.0.2.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        "alc_cerberus_utils",
        "alc_product_pharmacy",
        "alc_sale_channel",
        "authenticated_partner_mixin",
        "materialized_view_mixin",
        "sale_cancel_remaining",
        "pricelist_discount",  # discount_sale
        "product_additional",  # ratio_main_product
    ],
    "data": [
        "security/alc_eshop_product_ordered_qty.xml",
        "security/alc_eshop_product_ordered_yearly.xml",
        "data/ir_cron.xml",
    ],
    "demo": [],
    'installable': False
}
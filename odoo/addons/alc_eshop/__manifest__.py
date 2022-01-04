# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


{
    "name": "Alcyon E-Shop",
    "description": """Install all apps and modules required by Shopinvader""",
    "version": "10.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        "auth_jwt",
        "alc_pim",
        "alc_storage",
        "alc_eshop_filter_data",
        "alc_shopinvader_category",
        "shopinvader_elasticsearch",
        "shopinvader_product_stock",
        "shopinvader_multi_category",
        "shopinvader_assortment",
        "shopinvader_image",
        "shopinvader_sale_profile",
    ],
    "application": False,
    "data": [
        "data/auth_api_key.xml",
        "data/shopinvader_image_resize.xml",
        "data/shopinvader_assortment.xml",
        "data/product_pricelist.xml",
        "data/shopinvader_sale_profile.xml",
        "data/shopinvader_backend.xml",
    ],
    "demo": [],
}

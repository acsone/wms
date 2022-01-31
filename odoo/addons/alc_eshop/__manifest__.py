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
        "product_discount_specials",
        "alc_pim",
        "alc_storage",
        "alc_eshop_auth_jwt",
        "alc_eshop_cart_confirm",
        "alc_eshop_cart_recovery",
        "alc_eshop_filter_data",
        "alc_shopinvader_category",
        "shopinvader_auth_jwt",
        "shopinvader_elasticsearch",
        "shopinvader_product_stock_state",
        "shopinvader_multi_category",
        "shopinvader_assortment",
        "shopinvader_image",
        "shopinvader_sale_profile",
        "shopinvader_wishlist",
        "shopinvader_search_engine_update",
    ],
    "application": False,
    "data": [
        "data/auth_jwt_validator.xml",
        "data/shopinvader_image_resize.xml",
        "data/shopinvader_assortment.xml",
        "data/product_pricelist.xml",
        "data/shopinvader_sale_profile.xml",
        "data/shopinvader_backend.xml",
    ],
    "demo": [],
}

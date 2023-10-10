# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc App Eshop B2b",
    "description": """
        Gather all B2B related modules for Alcyon""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        # OCA/storage
        "fs_product_brand_multi_image",
        "fs_product_multi_image",
        "fs_product_multi_media",
        # ALC
        "alc_price_cache",
        "alc_price_cache_exclusive",
        "alc_product_assortment",
        "alc_base_multi_media_lang",
        "alc_eshop_classifieds",
        "alc_eshop_ads",
        "alc_eshop_classifieds_responsible",
        "alc_eshop_ordering_allowed",
    ],
    "data": [],
    "demo": [],
    "development_status": "Alpha",
}

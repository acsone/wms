# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alcyon ElasticSearch",
    "description": """Alcyon Shopinvader ElasticSearch Configuration""",
    "version": "10.0.1.0.3",
    "author": "ACSONE SA/NV",
    "website": "http://www.acsone.eu",
    "license": "AGPL-3",
    "category": "alc",
    "depends": [
        "alc_eshop",
        "alc_eshop_ads_elasticsearch",
        "alc_eshop_info_banner_elasticsearch",
        # removed "alc_eshop_product_image_sequence",
        "alc_older_stock_production_lot",
        "alc_partner_type",
        "alc_product_brand_image",
        "alc_product_pharmacy",
        "alc_product_mto",
        "alc_storage_media_lang",
        "alc_veterinary_group",
        "account_tax_one_vat",
    ],
    "data": [
        "data/ir_export_product.xml",
        "data/ir_export_category.xml",
        "data/se_backend.xml",
        "data/se_index_config_variants.xml",
        "data/se_index.xml",
    ],
    "post_init_hook": "post_init_hook",
    'installable': False
}
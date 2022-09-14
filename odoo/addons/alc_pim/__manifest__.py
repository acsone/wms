# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc PIM",
    "description": """Alcyon PIM""",
    "version": "10.0.1.0.3",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        "alc_pim_product",
        "alc_pim_attribute_group",
        "alc_product_shop_category",
        "alc_product_link_notice",
        "alc_storage_media_product",
        "product_animal_species",
        # data dependencies
        "product_dimension",
        "stock_production_lot_expiry",
        "specific_product",
        "specific_purchase",  # depends on alc_product_pharmacy, product_manufacturer
        "alc_product_audit",
        "product_brand",
    ],
    "application": False,
    "data": [
        "data/product_category.xml",
        "data/attribute_attribute.xml",
        "data/attribute_option.xml",
        "data/product_brand.xml",
        "views/product_category_views.xml",
        "views/product_template.xml",
    ],
    "demo": [],
    "pre_init_hook": "pre_init_hook",
    "post_init_hook": "post_init_hook",
    "external_dependencies": {"python": ["unicodecsv", "openupgradelib"]},
    'installable': False
}
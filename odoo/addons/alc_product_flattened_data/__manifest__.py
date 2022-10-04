# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Product Flattened Data",
    "description": """
        Alcyon: Materialized view to get accesse to flattened product's data in a efficient way""",
    "version": "10.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        "account_tax_one_vat",
        "alc_price_cache",
        "alc_product_shop_category",
        "alc_supplier_promotion",
        "materialized_view_mixin",
        "product_discount_specials",
        "product_multi_category",
        "queue_job_cron",
        "shopinvader",
        # create alc_product_supplier and remove this dependency (field supplier_id)
        "specific_purchase",
    ],
    "data": ["data/ir_cron.xml", "security/alc_product_flattened_data.xml"],
    "demo": [],
    "external_dependencies": {"python": ["ujson"]},
}

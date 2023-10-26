# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Product Flattened Data",
    "description": """
        Alcyon: Materialized view to get accesse to flattened product's data in a efficient way""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        "base_sparse_field",
        # OCA
        "product_multi_category",
        "account_tax_one_vat",
        "queue_job_cron",
        # ALC
        "alc_price_cache",
        "alc_product_additional_price",
        "alc_product_category_translatable",
        "alc_product_shop_category",
        "alc_product_web_publish",
        "alc_supplier_promotion",
        "alc_materialized_view_mixin",
        "alc_product_discount_special",
        "alc_pg_trgm",
    ],
    "data": ["data/ir_cron.xml", "security/alc_product_flattened_data.xml"],
    "demo": [],
    "external_dependencies": {"python": ["orjson"]},
}

# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Product Flattened Data",
    "description": """
        Alcyon: Materialized view to get accesse to flattened product's data in a efficient way""",
    "version": "16.0.1.0.1",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # fmt: off
        # Custom
        "alc_materialized_view_mixin",
        "alc_pg_trgm",
        "alc_price_cache",
        "alc_product_additional_price",
        "alc_product_category_translatable",
        "alc_product_discount_special",
        "alc_product_shop_category",
        "alc_product_web_publish",
        "alc_supplier_promotion",
        # OCA
        "account_tax_one_vat",
        "product_multi_category",
        "queue_job_cron",
        "shopinvader_base_url",
        # Others
        "base_sparse_field",
        # fmt: on
    ],
    "data": ["data/ir_cron.xml", "security/alc_product_flattened_data.xml"],
    "demo": [],
    "external_dependencies": {"python": ["orjson"]},
}

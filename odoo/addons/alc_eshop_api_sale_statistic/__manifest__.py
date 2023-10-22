# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Eshop Sale Stats",
    "description": """
        Alcyon: EShop services providing statistics on sales""",
    "version": "16.0.2.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        "alc_product_pharmacy",
        "alc_sale_channel",
        "alc_materialized_view_mixin",
        "sale_order_line_cancel",
        "alc_pricelist_discount",  # discount_sale
        # "product_additional",
        "alc_product_category_data",
        "alc_cerberus_utils",
        "fastapi",
    ],
    "data": [
        "security/alc_eshop_product_ordered_qty.xml",
        "security/alc_eshop_product_ordered_yearly.xml",
        "data/ir_cron.xml",
    ],
    "demo": [],
    "installable": True,
}

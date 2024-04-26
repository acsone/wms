# © 2018 Okia SPRL <Sylvain Van Hoof>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Alc purchase order builder",
    "version": "16.0.1.0.0",
    "author": "Okia SPRL,ACSONE SA/NV",
    "license": "AGPL-3",
    "category": "Others",
    "description": """
    Alc purchase order build
    """,
    "depends": [
        "alc_additional_product_base",
        "alc_product_average_sale",
        "alc_product_packaging",
        "alc_product_state",
        "alc_product_supplier",
        "alc_purchase_discount",
        "alc_purchase_order_total_weight",
        "alc_stock_lot_available",
        "alc_stock_orderpoint_product",
        "alc_supplier_promotion",
        "delivery",
        "product_expiry",
        "product_route_mto",
        "purchase",
        "stock_account",
        "stock_available",
        "stock_lot_is_archived",
        "stock_storage_type_putaway_abc",
        "alc_product_storage_temperature",
        "web",
    ],
    "assets": {
        "alc_purchase_order_builder.assets_purchase_order_builder": [
            "web/static/lib/Chart/Chart.js",
            "alc_purchase_order_builder/static/src/legacy/css/alc_purchase_order_builder.css",
            "alc_purchase_order_builder/static/src/legacy/js/alc_purchase_order_builder.js",
            "web/static/src/legacy/legacy_setup.js",
        ],
    },
    "data": ["views/purchase_order.xml", "views/templates.xml"],
    "external_dependencies": {"python": ["freezegun", "pytz"]},
    "pre_init_hook": "pre_init_hook",
    "website": "http://www.camptocamp.com",
    "installable": True,
}

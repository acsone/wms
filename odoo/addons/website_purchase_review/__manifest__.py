# © 2018 Okia SPRL <Sylvain Van Hoof>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Website purchase review",
    "version": "16.0.1.0.0",
    "author": "Okia SPRL,ACSONE SA/NV",
    "license": "AGPL-3",
    "category": "Others",
    "description": """
    Website purchase review
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
        "stock_storage_type_putaway_abc",
        "web",
    ],
    "assets": {
        "website_purchase_review.assets_website_purchase_review": [
            "web/static/lib/Chart/Chart.js",
            "website_purchase_review/static/src/legacy/css/purchase_review.css",
            "website_purchase_review/static/src/legacy/js/purchase_review.js",
            "web/static/src/legacy/legacy_setup.js",
        ],
    },
    "data": ["views/purchase_order.xml", "views/templates.xml"],
    "website": "http://www.camptocamp.com",
    "installable": True,
}

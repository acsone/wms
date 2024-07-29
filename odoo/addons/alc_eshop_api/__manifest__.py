# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Eshop Api",
    "description": """
        Alcyon: Eshop api""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # fmt: off
        # Custom
        "alc_eshop_api_cart",
        "alc_eshop_api_cart_delivery",
        "alc_eshop_api_cart_discount_pricelist",
        "alc_eshop_api_cart_product_unavailable",
        "alc_eshop_api_catalog",
        "alc_eshop_api_classifieds",
        "alc_eshop_api_cms",
        "alc_eshop_api_customer",
        "alc_eshop_api_delivery_carriers",
        "alc_eshop_api_discounts",
        "alc_eshop_api_documents",
        "alc_eshop_api_forms",
        "alc_eshop_api_orders",
        "alc_eshop_api_pickings",
        "alc_eshop_api_products_on_order",
        "alc_eshop_api_promotion_subscriptions",
        "alc_eshop_api_registration",
        "alc_eshop_api_sale_statistic",
        "alc_eshop_api_veterinary_groups",
        "alc_eshop_auth_jwt",
        "alc_eshop_sale_cart_channel",
        "alc_eshop_sale_cart_salesperson",
        "alc_eshop_schema_sale_channel",
        "alc_eshop_schema_sale_payment",
        "alc_eshop_schema_sale_product",
        "alc_eshop_schema_sale_product_unavailable",
        "alc_eshop_schema_sale_product_unavailable_pharmacy",
        "alc_eshop_schema_sale_qty_canceled",
        "alc_eshop_schema_sale_suite_name",
        "alc_eshop_schema_sale_triple_discount",
        # OCA
        "auth_jwt_server_env",
        "extendable_fastapi",
        "fastapi",
        "shopinvader_api_address",
        "shopinvader_api_cart",
        "shopinvader_api_sale",
        "shopinvader_api_wishlist",
        "shopinvader_fastapi_auth_jwt",
        # fmt: on
    ],
    "data": [
        "views/fastapi_endpoint.xml",
    ],
    "demo": [],
    "development_status": "Alpha",
}

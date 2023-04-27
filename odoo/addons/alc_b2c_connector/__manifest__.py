# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc B2C Connector",
    "description": """
        Alcyon: B2C Connector

        A set of FastAPI services used by B2C market places to makes SO.
        """,
    "version": "16.0.2.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        "fastapi",
        "product_assortment",
        "sale_channel",
        "sale_stock",
        "auth_api_key",
        "account_payment_mode",
        "alc_product_pharmacy",
        "stock_available",
        "alc_partner_type",
        "alc_b2c_partner",
        "sale_order_line_cancel",
        "account_payment_sale",
        "alc_sale_qty_returned",
        "alc_sale_product_qty_backorder",
        "delivery",
        "alc_product_pricelist_data",
        "alc_partner_suite",
        "stock_picking_backorder_reason",
        "alc_pricelist_discount",
        "alc_partner_pricelist",
        "alc_sale_channel",
    ],
    "data": [
        "security/fastapi_endpoint_settings.xml",
        "data/fastapi_endpoint.xml",
        "views/fastapi_endpoint_settings.xml",
        "views/fastapi_endpoint.xml",
        # "views/sale_order.xml",
        "data/ir_filters.xml",
        "data/product_pricelist.xml",
        "data/res_users.xml",
        # "views/alc_b2c_backend.xml",
        # "security/alc_b2c_backend.xml",
    ],
}

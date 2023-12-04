# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc B2C Connector",
    "description": """
        Alcyon: B2C Connector

        A set of FastAPI services used by B2C market places to makes SO.
        """,
    "version": "16.0.3.0.2",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # Odoo
        "sale_stock",
        "delivery",
        "snailmail",  # necessary dependency due to auto-install. This module override
        # partner write and perform search write on snailmail.letter
        # OCA
        "fastapi",
        "extendable_fastapi",
        "product_assortment",
        "sale_channel",
        "account_payment_mode",
        "stock_available",
        "account_payment_sale",
        "stock_picking_backorder_reason",
        "onchange_helper",
        "sale_exception",
        "sale_procurement_customer",
        "server_environment",
        # ALC
        "alc_product_pharmacy",
        "alc_partner_type",
        "alc_b2c_partner",
        "sale_order_line_cancel",
        "alc_sale_qty_returned",
        "alc_sale_product_qty_backorder",
        "alc_product_pricelist_data",
        "alc_partner_suite",
        "alc_pricelist_discount",
        "alc_partner_pricelist",
        "alc_sale_channel",
    ],
    "data": [
        "data/res_users.xml",
        "data/fastapi_endpoint.xml",
        "data/ir_filters.xml",
        "data/product_pricelist.xml",
        "security/groups.xml",
        "security/res_partner.xml",
        "security/sale_order.xml",
        "security/sale_order_line.xml",
        "security/alc_b2c_client.xml",
        "security/stock_picking.xml",
        "security/ir.model.access.csv",
        "views/fastapi_endpoint.xml",
        "views/alc_b2c_client.xml",
        "views/sale_order.xml",
    ],
    "demo": [],
    "post_init_hook": "post_init_hook",
    "application": True,
}

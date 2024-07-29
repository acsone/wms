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
        # fmt: off
        # Custom
        "alc_b2c_partner",
        "alc_partner_pricelist",
        "alc_partner_suite",
        "alc_partner_type",
        "alc_pricelist_discount",
        "alc_product_pharmacy",
        "alc_product_pricelist_data",
        "alc_sale_channel",
        "alc_sale_product_qty_backorder",
        "alc_sale_qty_returned",
        # OCA
        "account_payment_mode",
        "account_payment_sale",
        "extendable_fastapi",
        "fastapi",
        "onchange_helper",
        "product_assortment",
        "sale_channel",
        "sale_exception",
        "sale_order_line_cancel",
        "sale_procurement_customer",
        "server_environment",
        "stock_available",
        "stock_picking_backorder_reason",
        # Others
        "delivery",
        "sale_stock",
        "snailmail",
        # fmt: on
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

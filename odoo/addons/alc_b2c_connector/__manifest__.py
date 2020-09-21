# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc B2C Connector",
    "description": """
        Alcyon: ChronoVet Connector

        A set of REST services used by ChronoVet to makes PO.
        """,
    "version": "10.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        "account_payment_mode",
        "account_payment_sale",
        "alc_b2c_partner",
        "auth_api_key",
        "base_rest",
        "base_suspend_security",
        "connector",
        "onchange_helper",
        "procurement_sale",  # confirmation_date field on SO
        "product_assortment",
        "sale",
        "sale_confirm_background",
        "sales_team",
        "stock_available",
        "stock_picking_backorder",  # is_sale_back_order_accepted on respartner
        "specific_data",  # categs for product_assortment
        "specific_partner",  # alcyon_category_id on res_partner
        "specific_product",  # cnk_code on product
        "specific_sale",  # sale_channel field on SO
    ],
    "data": [
        "views/sale_order.xml",
        "data/ir_filters.xml",
        "data/product_pricelist.xml",
        "data/res_users.xml",
        "views/alc_b2c_backend.xml",
        "security/alc_b2c_backend.xml",
    ],
    "demo": [],
    "post_init_hook": "post_init_hook",
    "application": True,
}

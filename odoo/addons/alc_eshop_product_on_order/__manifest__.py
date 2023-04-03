# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Eshop Product On Order",
    "description": """
        Aclyon EShop: Products on order management services""",
    "version": "10.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        "alc_cerberus_utils",
        "alc_product_mto",
        "alc_product_pharmacy",
        "alc_sale_channel",
        "alc_sale_order_line_product_type",
        "authenticated_partner_mixin",
        "procurement_sale",  # TODO: partially replaced by alc_sale_product_qty_unavailable
        "sale_order_line_cancel",
        "sale_consignment",
        "alc_product_category_data",
    ],
    "data": ["data/mail_template.xml", "security/alc_eshop_product_on_order.xml"],
    "demo": [],
    'installable': False
}
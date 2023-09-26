# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Magento API Facade",
    "description": """Alcyon: Magento API Facade""",
    "version": "10.0.2.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        "alc_eshop",  # bring all fields
        "alc_eshop_services_catalog",
        "alc_eshop_services_deliveries",
        "alc_eshop_services_orders",
        "alc_eshop_sale_cart_info",
        "alc_product_flattened_data",
        "alc_sale_order_date_order_short",
    ],
    "demo": [],
    "external_dependencies": {"python": ["xmltodict", "dicttoxml"]},
    'installable': False
}
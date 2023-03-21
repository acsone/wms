# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Eshop Sale Cart Product Unavailable",
    "description": """
        Alcyon: Manage unavailable qty announcement into sale_cart process""",
    "version": "10.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        "procurement_sale",  # TODO: partially replaced by alc_sale_product_qty_unavailable
        "sale_cart_rest_api"
    ],
    "data": [],
    "demo": [],
    'installable': False
}
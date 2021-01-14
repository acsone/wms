# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Product Audit",
    "description": """
        Custom filter for Alcyon products""",
    "version": "10.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "depends": [
        "stock",
        "purchase",
        "product",
        "stock_orderpoint_product",
        "stock_product_bin",
        "specific_stock",
    ],
    "data": ["views/product_template.xml"],
    "demo": [],
}

# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Eshop Product Expiry",
    "description": """
        Alcyon: Keep the best_before_date in sync into the ES indexes""",
    "version": "10.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        "alc_older_stock_production_lot",
        "queue_job",
        "shopinvader_product_stock",
    ],
    "data": ["data/ir_export_product.xml"],
    "demo": [],
    'installable': False
}
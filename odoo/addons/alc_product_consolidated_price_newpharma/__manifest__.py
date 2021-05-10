# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Product Consolidated Price Newpharma",
    "description": """
        Alcyon: Daily generated consolidated price for NewPharma""",
    "version": "10.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        "alc_product_consolidated_price_report",
        "specific_data",
        "specific_product",
        "queue_job_cron",
    ],
    "data": ["data/ir_cron.xml", "data/ir_filters.xml"],
    "demo": [],
    "post_init_hook": "post_init_hook",
}

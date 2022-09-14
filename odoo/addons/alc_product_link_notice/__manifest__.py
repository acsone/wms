# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Product Notice",
    "description": """Alcyon Product Notice""",
    "version": "10.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": ["product", "queue_job"],
    "application": True,
    "data": [
        "data/ir_cron.xml",  # weekly check: create jobs
        "views/product_template.xml",
    ],
    "demo": [],
    "pre_init_hook": "pre_init_hook",
    'installable': False
}
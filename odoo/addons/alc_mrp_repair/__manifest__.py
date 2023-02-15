# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Mrp Repair",
    "description": """
        Alc MRP repair""",
    "version": "10.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "depends": ["mrp_repair"],
    "data": [
        "report/report_repair_order.xml",
        "report/report_repairorder_document.xml",
        "data/sav_location.xml",
        "data/mail_template.xml",
        "views/mrp_repair.xml",
    ],
    "demo": [],
    "pre_init_hook": "pre_init_hook",
    'installable': False
}
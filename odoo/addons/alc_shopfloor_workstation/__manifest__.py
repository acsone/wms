# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Shopfloor Workstation",
    "description": """
        Alcyon: Shopfloor Workstation""",
    "version": "10.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        "alc_package_label_printer",  # replaced by base_report_to_label_printer
        "alc_product_label_printer",
        "shopfloor_workstation",
    ],
    "data": ["views/shopfloor_workstation.xml"],
    "demo": [],
    'installable': False
}
# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Turnover Reporting",
    "description": """
        Generate turnover reports""",
    "version": "10.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "depends": ["account", "stock", "sale", "stock_delivery_note"],
    "data": ["wizards/export_report_turnover.xml"],
    "demo": [],
    "external_dependencies": {"python": ["pandas", "numpy"]},
}

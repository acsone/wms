# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Stock Negative Quant Audit",
    "description": """
        Alcyon: Logs creation and stacktrace of negative quants creation""",
    "version": "10.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": ["stock"],
    "data": [
        "security/stock_negative_quant_audit.xml",
        "views/stock_negative_quant_audit.xml",
    ],
    "demo": [],
}

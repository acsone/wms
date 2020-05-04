# -*- coding: utf-8 -*-
# Copyright 2020 Acsone SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Analytic Category Report",
    "description": """
        Add a new view for account analytics using 3 columns for tags""",
    "version": "10.0.1.0.0",
    "license": "AGPL-3",
    "author": "Acsone SA/NV",
    "website": "http://acsone.eu",
    "depends": ["analytic"],
    "data": [
        "views/account_analytic_account.xml",
        "views/account_move_line_with_analytic_categories.xml",
        "security/ir.model.access.csv",
    ],
    "demo": [],
}

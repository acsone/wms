# Copyright 2020 Acsone SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Analytic Category Report",
    "description": """
        Add a new view for account analytics using 3 columns for tags""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "http://acsone.eu",
    "depends": [
        # fmt: off
        # Custom
        "account_move_line_single_analytic_account",
        # OCA
        "account_analytic_account_tag",
        # fmt: on
    ],
    "data": [
        "views/account_analytic_account_views.xml",
        "views/account_move_line_with_analytic_categories_views.xml",
        "security/ir.model.access.csv",
    ],
    "demo": [],
    "installable": True,
}

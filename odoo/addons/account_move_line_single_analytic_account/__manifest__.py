# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Account Move Line Single Analytic Account",
    "description": """Restore the analytic_account_id on account.move.line""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # Others
        "account",
    ],
    "data": ["views/account_move_line_views.xml"],
    "demo": [],
    "installable": True,
}

# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Stock Move Line User",
    "description": """
        Alcyon: Audit operator activity""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": ["stock"],
    "data": [
        "security/alc_stock_move_line_audit.xml",
        "views/alc_stock_move_line_audit.xml",
    ],
    "demo": [],
}

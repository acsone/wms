# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Turnover Reporting",
    "description": """
        Generate turnover reports""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "depends": [
        # Others
        "account",
        "sale",
        "sale_stock",
        "stock",
    ],
    "data": [
        "wizards/export_report_turnover.xml",
        "security/export_report_turnover.xml",
    ],
    "demo": [],
    "external_dependencies": {"python": ["pandas", "numpy"]},
    "installable": True,
}

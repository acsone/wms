# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Printing Base",
    "summary": """
        Foundation of printing for Alcyon""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # OCA
        "base_report_to_printer",
    ],
    "data": ["views/printing_printer_views.xml"],
    "demo": [],
    "installable": True,
    "pre_init_hook": "pre_init_hook",
}

# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Report Stock Picking Operations",
    "summary": """
        Stock picking operations reporting for Alcyon""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # fmt: off
        # Custom
        "alc_report_base",
        # Others
        "stock",
        # fmt: on
    ],
    "data": [
        "views/report_stock_picking_operations.xml",
    ],
    "demo": [],
    "installable": True,
}

# Copyright 2023 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Alc Stock Picking Responsible Portal",
    "description": """
        Alcyon: allow to select a portal user as responsible in stock picking""",
    "version": "16.0.1.0.0",
    "license": "LGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # Others
        "stock",
    ],
    "data": [
        "views/stock_picking_views.xml",
    ],
    "demo": [],
    "installable": True,
}

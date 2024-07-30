# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Stock Scrap Responsible",
    "description": """
        Add responsible field on stock scrap""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # Others
        "stock",
    ],
    "data": [
        "views/stock_scrap.xml",
    ],
    "demo": [],
    "pre_init_hook": "pre_init_hook",
    "installable": True,
}

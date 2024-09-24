# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Empty Package At Picking Return",
    "description": """
        This addon adds a setting to the picking type to enable package empty during
        picking return""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        # OCA
        "rma",
        # Others
        "stock",
    ],
    "data": [
        "views/stock_picking_type.xml",
    ],
    "demo": [],
}

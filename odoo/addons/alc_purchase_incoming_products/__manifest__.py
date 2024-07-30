# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Purchase Incoming Products",
    "description": """
        This addon adds the capability to list all incoming products""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        # Others
        "purchase",
        "stock",
    ],
    "data": [
        "views/stock_move_views.xml",
        "views/purchase_views.xml",
    ],
}

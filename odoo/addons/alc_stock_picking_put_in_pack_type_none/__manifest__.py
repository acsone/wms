# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Stock Picking Put In Pack Type None",
    "description": """
        This module allows to allow to use package types with no carrier integration in picking flows""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        # OCA
        "stock_picking_delivery_link",
    ],
    "data": [
        "views/stock_picking_type.xml",
    ],
}

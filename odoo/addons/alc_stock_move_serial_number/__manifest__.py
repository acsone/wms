# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Stock Move Serial Number",
    "summary": """
        This module adds a serial_number to the stock move.
        The information is useful and used for delivery orders.""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        # fmt: off
        # Others
        "stock",
        # fmt: on
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/stock_picking_views.xml",
        "views/stock_picking_type.xml",
        "wizards/modify_serial_number_views.xml",
    ],
}

# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Stock Location Orderpoint Priority",
    "description": """
        Allows to set to maximum priority merged moved linked to location orderpoints""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        # fmt: off
        # OCA
        "stock_location_orderpoint",
        "stock_move_manage_priority",
        "stock_move_priority_picking_assign",
        # fmt: on
    ],
}

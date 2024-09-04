# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Test Alcyon Shopfloor Reassort",
    "description": """Tests for reassort using Shopfloor""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        # Custom
        "alc_stock_move_line_restrict_quantity",
        # OCA
        "shopfloor_full_location_reservation",
        "stock_full_location_reservation",
        "stock_location_orderpoint",
    ],
}

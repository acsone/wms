# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Sale Mto Check Procurements",
    "description": """
        Check reordering rule whenever a product with the MTO route is sold""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        # Custom
        "alc_stock_scheduler_filter",
        # Others
        "sale",
    ],
    "data": [],
    "demo": [],
}

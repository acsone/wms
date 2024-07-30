# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Sale Order Sort By Date Order",
    "description": """
        This modules ensures that sale orders are sorted by date_order in the list views.""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        # OCA
        "sale_exception",
    ],
    "data": ["views/sale_order_views.xml"],
    "demo": [],
}

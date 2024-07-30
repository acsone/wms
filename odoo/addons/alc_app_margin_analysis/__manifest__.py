# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc App Margin Analysis",
    "description": """
        Add sale margin capabitlities to odoo""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://www.acsone.eu",
    "development_status": "Alpha",
    "depends": [
        # Custom
        "alc_sale_margin",
        # OCA
        "sale_margin_delivered_dropshipping",
        "sale_margin_delivered_security",
    ],
    "data": [],
    "demo": [],
    "application": True,
    "installable": True,
}

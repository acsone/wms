# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc App Margin Analysis",
    "description": """
        Add sale margin capabitlities to odoo""",
    "version": "16.0.1.0.1",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://www.acsone.eu",
    "development_status": "Alpha",
    "depends": [
        # Third-party
        "sale_margin_delivered_dropshipping",
        "sale_margin_delivered_security",
        "sale_order_blanket_order_sale_margin",
        # Alcyon
        "alc_sale_margin",
    ],
    "data": [],
    "demo": [],
    "application": True,
    "installable": True,
}

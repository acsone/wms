# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Deliveries Webservice",
    "description": """Alcyon: Deliveries Webservices""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # Odoo Community
        "stock",
        # Third-party
        "fastapi",
        "stock_procurement_customer",
        # Alcyon
        "alc_cerberus_utils",
        # Alcyon/Stock
        "alc_stock_delivery_slip",
    ],
    "demo": [],
    "installable": True,
}

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
        # Custom
        "alc_cerberus_utils",
        "alc_stock_delivery_slip",
        # OCA
        "fastapi",
        "stock_procurement_customer",
        # Others
        "stock",
    ],
    "demo": [],
    "installable": True,
}

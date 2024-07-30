# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Product Lot Info",
    "description": """
        Alcyon: Display lots on product form view""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # Custom
        "alc_stock_lot_available",
        # Others
        "product_expiry",
        "stock",
    ],
    "data": ["views/product_template_views.xml"],
    "demo": [],
    "installable": True,
}

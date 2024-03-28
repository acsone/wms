# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Sale Order Line Lots",
    "description": """
        Add a lots field on sale order lines""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": ["sale", "alc_stock_lot_available", "alc_older_stock_production_lot"],
    "data": [
        "views/sale_order.xml",
        "views/stock_lot.xml",
    ],
    "demo": [],
}

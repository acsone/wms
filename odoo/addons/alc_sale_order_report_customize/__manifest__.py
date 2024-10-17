# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Sale Order Report Customize",
    "description": """
        Customize the sale order document""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        # Alcyon
        "alc_sale_product_qty_unavailable",
        # Alcyon/Sales Management
        "alc_pricelist_discount",
    ],
    "data": ["reports/sale_order.xml"],
    "demo": [],
}

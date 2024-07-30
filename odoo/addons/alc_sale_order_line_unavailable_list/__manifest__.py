# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Sale Order Line Unavailable List",
    "description": """
        This addon add a menu entry for all Unavailable sale order lines""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        # Custom
        "alc_sale_consignment",
        # OCA
        "sale_order_line_cancel",
    ],
    "data": ["views/sale_order_line.xml"],
    "demo": [],
}

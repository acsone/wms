# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Sale Exception Product Availability",
    "description": """
        Alcyon specific sale exceptions for product availability""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        "sale_stock",
        "stock",
        "stock_available",
        "stock_picking_backorder_reason",
        "alc_sale_product_qty_unavailable",
        "alc_product_state",
        "alc_sale_exception",  # warning text
        "alc_sale_exception_settings",
    ],
    "data": ["data/exception_rule.xml"],
    "pre_init_hook": "pre_init_hook",
}

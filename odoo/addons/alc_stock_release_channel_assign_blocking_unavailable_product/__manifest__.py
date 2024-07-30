# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Stock Release Channel Assign Blocking Unavailable Product",
    "description": """
        Block delivery of unavailable products when the unavailability
        has been announced on the SO""",
    "version": "16.0.1.0.2",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        # Custom
        "alc_sale_product_qty_unavailable",
        # OCA
        "stock_release_channel",
        # Others
        "sale_stock",
    ],
    "data": ["views/sale_order.xml", "views/stock_picking.xml"],
}

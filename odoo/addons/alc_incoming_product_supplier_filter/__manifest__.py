# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Incoming Product Supplier Filter",
    "description": """
        Add a filter on incoming products to filter them by supplier""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "depends": [
        # fmt: off
        # Custom
        "alc_product_supplier",
        # Others
        "stock",
        # fmt: on
    ],
    "data": ["views/stock_move_views.xml"],
    "demo": [],
    "installable": True,
}

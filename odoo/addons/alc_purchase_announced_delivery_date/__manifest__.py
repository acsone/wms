# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Purchase Announced Delivery Date",
    "description": """
        Add an announced date on the purchase order lines""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "depends": [
        # fmt: off
        # Others
        "purchase_stock",
        # fmt: on
    ],
    "data": ["views/purchase_order_views.xml"],
    "demo": [],
    "installable": True,
}

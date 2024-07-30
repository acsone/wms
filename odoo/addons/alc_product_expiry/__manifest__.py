# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Product Expiry",
    "description": """
        exclude expired lots during availability checks""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        # OCA
        "stock_available_to_promise_release",
        # Others
        "product_expiry",
    ],
    "data": [
        "views/stock_picking.xml",
        "views/stock_picking_type.xml",
    ],
    "demo": [],
}

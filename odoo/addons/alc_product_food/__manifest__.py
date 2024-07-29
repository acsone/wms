# Copyright 2023 ACSONE
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Product Food",
    "description": """
        Add an is_food flag on product templates""",
    "version": "16.0.1.0.0",
    "license": "LGPL-3",  # MUST BE LGPL so alc_stock_receive_lot can depend on it
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        # fmt: off
        # Others
        "stock_account",
        # fmt: on
    ],
    "data": ["data/product_category.xml"],
    "demo": [],
}

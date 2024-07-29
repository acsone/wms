# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Stock Move Location By Supplier",
    "description": """
        Alcyon: Allows to move generate a picking to move a location with product from specific supplier""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://www.acsone.eu",
    "depends": [
        # fmt: off
        # Custom
        "alc_product_supplier",
        # OCA
        "stock_move_location",
        # fmt: on
    ],
    "data": [
        "wizards/wiz_stock_move_location.xml",
    ],
    "demo": [],
}

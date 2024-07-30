# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Product Search More Tree View",
    "description": """
        This addon add a dedicated tree view for product when user select search more option""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        # OCA
        "product_stock_state",
        # Others
        "purchase",
        "sale",
    ],
    "data": [
        "views/purchase_order.xml",
        "views/product_product.xml",
        "views/sale_order.xml",
    ],
    "demo": [],
}

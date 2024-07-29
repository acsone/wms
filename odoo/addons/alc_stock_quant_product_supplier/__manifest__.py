# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Stock Quant Product Supplier",
    "description": """
        This addons adds the product supplier to stock quant""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        # fmt: off
        # Custom
        "alc_product_supplier",
        # Others
        "stock",
        # fmt: on
    ],
    "data": ["views/stock_quant.xml"],
    "demo": [],
}

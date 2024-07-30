# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Search By Vendor Product Code",
    "description": """
        This models allows searching different models related to `product.product`
        with its `vendor_product_code` field""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        # Custom
        "alc_product_supplier",
        # Others
        "product",
        "stock",
    ],
    "data": [],
    "demo": [],
}

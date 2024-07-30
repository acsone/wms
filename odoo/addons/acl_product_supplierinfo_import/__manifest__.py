# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Acl Product Supplierinfo Import",
    "description": """
        This addon allows product supplierinfo import using cnk_code or product code""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        # Custom
        "alc_product_pharmacy",
        "alc_product_supplier",
        "alc_product_supplierinfo_default_price",
    ],
    "data": ["views/product_supplierinfo.xml"],
    "demo": [],
}

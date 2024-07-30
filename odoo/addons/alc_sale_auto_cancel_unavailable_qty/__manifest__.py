# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Sale Auto Cancel Unavailable Qty",
    "description": """
        Automatically cancel unavailable ordered quantity to avoid the generation of backorders
 """,
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        # Custom
        "alc_sale_product_qty_unavailable",
        # Others
        "stock",
    ],
    "data": ["views/res_partner.xml"],
    "demo": [],
}

# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Sale Order Line Unavailable",
    "description": """
        On a """,
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        # Custom
        "alc_sale_order_line_unavailable_list",
        "alc_sales_count",
    ],
    "data": [
        "views/res_partner.xml",
        "views/product_template.xml",
        "views/product_product.xml",
    ],
    "demo": [],
}

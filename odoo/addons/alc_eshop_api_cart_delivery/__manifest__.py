# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Sale Cart Delivery Rest Api",
    "summary": """
        Manage deliveries on sale.cart""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "depends": [
        # fmt: off
        # Custom
        "alc_eshop_delivery_method",
        "alc_eshop_schema_sale_delivery",
        # OCA
        "fastapi",
        "onchange_helper",
        "shopinvader_sale_cart",
        # Others
        "delivery",
        # fmt: on
    ],
    "data": [],
    "demo": [],
    "installable": True,
    "development_status": "Alpha",
}

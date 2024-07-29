# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Purchase Order Discount",
    "description": """
        This addon define purchase orders discount""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        # fmt: off
        # OCA
        "purchase_discount",
        # fmt: on
    ],
    "data": [
        "views/res_partner.xml",
        "views/purchase_order_line.xml",
        "views/purchase_order.xml",
    ],
    "demo": [],
}

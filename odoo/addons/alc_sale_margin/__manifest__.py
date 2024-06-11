# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Sale Margin",
    "description": """
        Add margin on sale order line""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://www.acsone.eu",
    "depends": [
        "sale_margin_delivered",
    ],
    "data": [
        "views/sale_order_line.xml",
    ],
    "demo": [],
    "installable": True,
}

# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Eshop Sale Qty Cancelled",
    "description": """
        Alcyon: Add cancelled qty into line info""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # OCA
        "sale_order_line_cancel",
        "shopinvader_schema_sale",
    ],
    "data": [],
    "demo": [],
    "installable": True,
    "development_status": "Alpha",
}

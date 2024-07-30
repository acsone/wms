# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Eshop Sale Cart Channel",
    "description": """
        Alcyon: Add sale channel to cart schema""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # OCA
        "sale_shipping_info_helper",
        "shopinvader_schema_sale",
        # Others
        "delivery",
    ],
    "data": [],
    "demo": [],
    "installable": True,
    "development_status": "Alpha",
}

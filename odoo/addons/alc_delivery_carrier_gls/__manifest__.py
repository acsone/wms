# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Delivery Carrier Gls",
    "description": """
        Alcyon: Add GLS delivery carriers""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # OCA
        "delivery_carrier_label_gls",
    ],
    "data": ["data/product_product.xml", "data/delivery_carrier.xml"],
    "demo": [],
    "installable": True,
}

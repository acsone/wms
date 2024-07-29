# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Older Stock Production Lot",
    "description": """
        Alcyon: Managed older production lot available for a product""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # fmt: off
        # Custom
        "alc_stock_location_data",
        # Others
        "product_expiry",
        # fmt: on
    ],
    "data": [],
    "demo": [],
    "installable": True,
}

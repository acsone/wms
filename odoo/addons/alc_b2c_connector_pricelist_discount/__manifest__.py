# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc B2c Connector Pricelist Discount",
    "description": """
        Alcyon: Pricelist discount for B2C SO""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # fmt: off
        # Custom
        "alc_b2c_connector",
        "alc_pricelist_discount",
        # fmt: on
    ],
    "data": ["views/alc_b2c_client.xml"],
    "demo": [],
}

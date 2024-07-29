# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Partner Force Re Geolocalization",
    "description": """
        Alcyon: Force to re geolocalize the partner if address has change""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # fmt: off
        # Custom
        "alc_b2c_partner",
        # Others
        "account",
        # fmt: on
    ],
    "data": ["views/res_partner.xml"],
    "demo": [],
    "installable": True,
}

# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc B2C App",
    "description": """
        Gather all b2c related modules for Alcyon""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "application": True,
    "depends": [
        # ALC
        "alc_b2c_connector",
        "alc_chronovet",
        "alc_clubvetshop",
        "alc_placedesvetos",
        "alc_logiweb",
    ],
}

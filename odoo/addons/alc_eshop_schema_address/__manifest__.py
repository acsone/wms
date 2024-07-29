# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Eshop Schema Address",
    "description": """
        Alcyon: Add veterinary info on address info into the eshop""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # fmt: off
        # Custom
        "alc_partner_opt_out",
        "alc_partner_veterinary",
        # OCA
        "shopinvader_schema_address",
        # fmt: on
    ],
    "data": [],
    "demo": [],
    "installable": True,
}

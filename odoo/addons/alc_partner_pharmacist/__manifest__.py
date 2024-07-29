# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Partner Pharmacist",
    "description": """
        Add pharmacist info to contacts""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        # fmt: off
        # OCA
        "partner_manual_rank",
        # fmt: on
    ],
    "data": [
        "views/res_partner.xml",
    ],
    "demo": [],
}

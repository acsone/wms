# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Sale Auto Subscribe",
    "description": """
        Alcyon: Auto subscribe specific user to sale order discussion""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://www.acsone.eu",
    "depends": [
        # fmt: off
        # Custom
        "alc_partner_type",
        # Others
        "sale",
        # fmt: on
    ],
    "data": [
        "data/res_users.xml",
    ],
    "demo": [],
}

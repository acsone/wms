# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Allow/Disallow eshop ordering",
    "description": """
        Alcyon: Add flag to allow/disallow a partner to pass an order on the
        eshop.
        """,
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # fmt: off
        # Others
        "base",
        # fmt: on
    ],
    "data": ["views/res_partner.xml"],
    "demo": [],
    "installable": True,
}

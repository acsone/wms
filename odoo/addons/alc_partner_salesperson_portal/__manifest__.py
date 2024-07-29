# Copyright 2023 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Alc Partner Salesperson Portal",
    "description": """
        Alcyon: allow to select a portal user as Sales person in contact""",
    "version": "16.0.1.0.0",
    "license": "LGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # fmt: off
        # Others
        "base",
        # fmt: on
    ],
    "data": [
        "views/res_partner_views.xml",
    ],
    "demo": [],
    "installable": True,
}

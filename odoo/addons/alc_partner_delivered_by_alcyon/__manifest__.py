# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Partner Delivered By Alcyon",
    "description": """
        Alcyon: Add the is_delivered_by_alcyon field on partner""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # Others
        "base",
    ],
    "data": [
        "views/res_partner_views.xml",
    ],
    "demo": [],
    "installable": True,
}

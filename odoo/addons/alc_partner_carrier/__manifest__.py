# Copyright 2021 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Alc Partner Carrier",
    "description": """
        Alcyon: Add a flag on partners how are carriers""",
    "version": "16.0.1.0.0",
    "license": "LGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # Others
        "base",
    ],
    "data": [
        "views/res_partner_views.xml",
        "data/res_partner_category.xml",
    ],
    "demo": [],
    "installable": True,
}

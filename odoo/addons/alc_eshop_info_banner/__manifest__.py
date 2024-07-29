# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Eshop Info Banner",
    "description": """
        Alcyon: Manage info banner displayed on each page of the website""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # fmt: off
        # Others
        "sales_team",
        # fmt: on
    ],
    "data": [
        "security/res_groups.xml",
        "security/alc_eshop_info_banner.xml",
        "views/alc_eshop_info_banner.xml",
    ],
    "demo": [],
    "installable": True,
}

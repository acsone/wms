# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Eshop Ads",
    "description": """
        Alcyon: Manage ads on eshop""",
    "version": "16.0.1.0.1",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # Custom
        "mixin_past",
        # OCA
        "fs_image",
        # Others
        "sales_team",
    ],
    "data": [
        "security/res_groups.xml",
        "security/alc_eshop_ads.xml",
        "views/alc_eshop_ads.xml",
    ],
    "development_status": "Alpha",
    "installable": True,
}

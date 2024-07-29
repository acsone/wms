# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Sale Exception Settings",
    "description": """
        Alc Sale Exception: Add setting to activate exception checks (disable by default)
        and """,
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # fmt: off
        # OCA
        "sale_exception",
        # fmt: on
    ],
    "data": [
        "views/res_config_settings.xml",
    ],
    "demo": [],
    "installable": True,
}

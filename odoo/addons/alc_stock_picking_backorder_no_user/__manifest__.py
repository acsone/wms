# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Stock Picking Backorder No User",
    "description": """
        Allows to void the user affected to the backorder in that case.""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        # fmt: off
        # Others
        "stock",
        # fmt: on
    ],
    "data": [
        "views/res_config_settings.xml",
    ],
}

# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Stock Location Constraint",
    "description": """
        Allows to define a unique constraint on stock location based on its characteristics""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        # fmt: off
        # OCA
        "stock_location_position",
        "stock_location_zone",
        # fmt: on
    ],
    "data": [
        "views/res_config_settings.xml",
    ],
}

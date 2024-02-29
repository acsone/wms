# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Stock Move Line Restrict Quantity",
    "description": """
        This module allows to trace stock move line quantity change to zero or a negative one""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        "stock",
    ],
    "data": ["views/res_config_settings.xml"],
}

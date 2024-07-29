# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Account Tax Precision",
    "description": """
        Allows to define specific tax decimal precision""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "Camptocamp,ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        # fmt: off
        # Others
        "account",
        # fmt: on
    ],
    "data": ["data/decimal_precision.xml"],
}

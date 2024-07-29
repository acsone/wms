# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Stock Location Data",
    "description": """
        This addon add default alcyon locations""",
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
    "data": ["data/stock_location.xml"],
    "pre_init_hook": "pre_init_hook",
}

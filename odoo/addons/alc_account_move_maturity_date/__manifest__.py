# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Account Move Maturity Date",
    "description": """
        Allows to get a maturity date on account move that are generated in some defined journals""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        "account",
    ],
    "data": ["views/account_journal.xml"],
}

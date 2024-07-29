# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Res Company Terms Condition",
    "description": """
        This addon adds invoice and delivery terms conditions""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        # fmt: off
        # Others
        "base",
        # fmt: on
    ],
    "data": ["views/res_company.xml"],
    "pre_init_hook": "pre_init_hook",
}

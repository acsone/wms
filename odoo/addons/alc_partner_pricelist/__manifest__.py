# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Partner Price list",
    "description": """
        This addon define allowed price lists for partners""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        # fmt: off
        # Others
        "sale",
        # fmt: on
    ],
    "data": ["views/res_partner.xml"],
    "demo": [],
    "pre_init_hook": "pre_init_hook",
}

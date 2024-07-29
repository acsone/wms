# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Eshop Salesperson",
    "description": """Alcyon: Eshop Salesperson""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # fmt: off
        # OCA
        "shopinvader_sale_cart",
        # fmt: on
    ],
    "data": ["data/res_users.xml"],
    "demo": [],
    "installable": True,
    "pre_init_hook": "pre_init_hook",
}

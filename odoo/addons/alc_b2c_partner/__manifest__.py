# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc B2c Partner",
    "description": """Alcyon: Add B2C category for patners""",
    "version": "16.0.2.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # fmt: off
        # Custom
        "alc_partner_manual_sale_order",
        # fmt: on
    ],
    "data": [
        "data/res_partner_category.xml",
        "data/res_partner.xml",
        "views/res_partner.xml",
    ],
}

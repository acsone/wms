# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Eshop Total Year End Rebate Partner Visibility",
    "summary": """Allows partner to get access to the total of cumulated rfa from the website""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        # Alcyon
        "alc_veterinary_group",
    ],
    "data": [
        "views/res_partner.xml",
    ],
    "demo": [],
}

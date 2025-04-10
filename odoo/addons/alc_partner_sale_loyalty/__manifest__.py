# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Partner Sale Loyalty",
    "summary": """Alcyon: Add link from partner to layalty card""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        # Third-party
        "sale_loyalty_beneficiary",
    ],
    "data": [
        "views/res_partner.xml",
    ],
    "demo": [],
}

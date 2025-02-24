# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Sale Loyalty Year End Rebate Applicability",
    "summary": """Manage retroactive application of a program when adding a new beneficiary""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        # Third-party
        "loyalty_partner_applicability",
        "sale_loyalty_initial_date_validity",
        # Alcyon
        "alc_sale_loyalty_year_end_rebate",
        "alc_veterinary_group",
    ],
    "data": [],
    "demo": [],
}

# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Sale Loyalty Rfa Updater",
    "summary": """Add Update Wizard for RFA loyalty rules""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        # Third-party
        "sale_loyalty_initial_date_validity",
        # Alcyon
        "alc_sale_loyalty_year_end_rebate",
    ],
    "data": [
        "views/loyalty_program.xml",
        "wizards/al_loyalty_rule_updater.xml",
        "wizards/al_loyalty_rule_updater_line.xml",
        "security/alc_loyalty_rule_updater.xml",
    ],
    "demo": [],
}

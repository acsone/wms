# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Sale Stock Loyalty Year End Rebate",
    "summary": """Compute point on deliverd qty""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        # Odoo Community
        "sale_stock",
        # Third-party
        "base_partition",
        # Alcyon
        "alc_sale_loyalty_year_end_rebate",
    ],
    "data": ["views/loyalty_card.xml"],
    "demo": [],
}

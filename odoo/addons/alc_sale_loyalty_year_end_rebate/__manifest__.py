# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Sale Loyalty Rfa",
    "summary": """Add RFA loyalty program""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        # Odoo Community
        "sale_loyalty",
        # Third-party
        "base_partition",
        "base_view_inheritance_extension",
        "sale_loyalty_beneficiary",
        "sale_loyalty_partner_applicability",
        # Alcyon
        "alc_loyalty_info",
        "alc_queue_job_background_channel",
    ],
    "data": [
        "views/loyalty_rule.xml",
        "data/queue_job_function.xml",
    ],
    "demo": [],
}

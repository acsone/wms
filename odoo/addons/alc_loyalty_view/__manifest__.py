# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Loyalty View",
    "summary": """Alcyon: Specialized view for loyalty programs""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        # Odoo Community
        "loyalty",
        # Third-party
        "base_view_inheritance_extension",
        # Alcyon
        "alc_loyalty_info",
    ],
    "data": [
        "views/loyalty_program.xml",
    ],
    "demo": [],
}

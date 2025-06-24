# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Base Security",
    "summary": """Specific ACL for base models""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # Odoo Community
        "base",
    ],
    "data": [
        "security/res_groups.xml",
        "security/ir.model.access.csv",
    ],
    "demo": [],
}

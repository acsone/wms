# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Purchase Order Date Planned",
    "description": """
        This addon enhance purchase order date planned calculation""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        # OCA
        "hr_holidays_public",
        # Others
        "purchase",
    ],
    "data": ["views/res_partner.xml"],
}

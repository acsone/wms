# Copyright 2021 Acsone SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Customer Invoices By Fiscal Year",
    "description": """
        Compute customer invoices and totals by fiscal years""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "depends": [
        # Others
        "account",
    ],
    "data": ["views/res_partner.xml"],
    "demo": [],
}

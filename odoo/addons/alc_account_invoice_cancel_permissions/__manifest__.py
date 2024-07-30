# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Account Invoice Cancel Permissions",
    "description": """
        Add permissions on users to cancel invoices""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "depends": [
        # Others
        "account",
    ],
    "data": ["security/res_groups.xml", "views/account_move.xml"],
    "demo": [],
}

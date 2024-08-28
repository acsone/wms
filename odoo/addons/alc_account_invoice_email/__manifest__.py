# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Account Invoice Email",
    "description": "Account Invoice Email",
    "version": "16.0.1.0.3",
    "author": "ACSONE SA/NV",
    "license": "AGPL-3",
    "category": "Accounting & Finance",
    # mail dependency is needed as mail module replaces the email field...
    "depends": [
        # Others
        "account",
        "mail",
    ],
    "data": ["data/mail_template.xml", "views/res_partner.xml"],
    "installable": True,
}

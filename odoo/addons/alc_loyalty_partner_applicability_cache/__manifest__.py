# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Loyalty Partner Applicability Cache",
    "summary": """Alcyon, store beneficialry partner on loyalty program

    This addon maintains a list of beneficialry partners on loyalty program
    even if the program only defines a domain on the partner

    In the case where no restriction is defined on loyalty program, this
    list is empty.
    """,
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        # Third-party
        "loyalty_partner_applicability",
    ],
    "data": [
        "data/ir_cron.xml",
    ],
    "demo": [],
}

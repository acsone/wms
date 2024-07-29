# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Account Move Default Reference Type",
    "description": """
        This addon allows setting a default value for the invoice reference type at the
        partner level.""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        # fmt: off
        # OCA
        "account_payment_order",
        # fmt: on
    ],
    "data": [
        "views/res_partner.xml",
    ],
    "demo": [],
}

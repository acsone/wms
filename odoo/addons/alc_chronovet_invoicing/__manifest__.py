# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Chronovet Invoicing",
    "description": """
        Alcyon; Chronovet Invoicing""",
    "version": "10.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        "account",
        "account_banking_sepa_direct_debit",
        "account_payment_mode",
        "account_payment_sale",
    ],
    "data": ["data/account_payment_mode.xml"],
    "demo": [],
}

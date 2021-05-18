# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Placedesvetos",
    "description": """
        B2C connector for Place des Vétos""",
    "version": "10.0.2.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        "alc_b2c_connector",
        "alc_b2c_connector_pricelist_discount",
        "account_banking_sepa_direct_debit",
        "account_payment_mode",
    ],
    "data": [
        "data/account_payment_mode.xml",
        "data/auth_api_key.xml",
        "data/alc_b2c_backend.xml",
        "data/res_partner.xml",
    ],
    "demo": [],
}

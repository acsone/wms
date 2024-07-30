# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Placedesvetos",
    "description": """
        B2C connector for Place des Vétos""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # Custom
        "alc_b2c_connector",
        "alc_b2c_connector_pricelist_discount",
        "alc_product_pricelist_data",
        # OCA
        "account_banking_sepa_direct_debit",
        "account_payment_mode",
        "account_payment_order",
        "account_payment_partner",
    ],
    "data": [
        "data/account_payment_mode.xml",
        "data/res_partner.xml",
        "data/sale_channel.xml",
        "data/alc_b2c_client.xml",
    ],
    "demo": [],
    "installable": True,
}

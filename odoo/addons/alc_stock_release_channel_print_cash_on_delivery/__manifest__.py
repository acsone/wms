# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Stock Release Channel Print Cash Invoices",
    "description": """This module allows users to print cash on delivery invoices
    from a release channel.""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        "stock_release_channel_shipment_advice_deliver",
        "partner_invoicing_mode_cash_on_delivery",
    ],
    "data": ["views/stock_release_channel.xml"],
    "demo": [],
}

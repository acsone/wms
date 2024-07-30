# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Stock Release Channel Deliver Gls",
    "description": """
        This addon add an extra check for release channels deliver if it contains gls
        pickings""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        # OCA
        "delivery_carrier_label_gls",
        "stock_release_channel_shipment_advice_deliver",
    ],
    "data": [],
    "demo": [],
}

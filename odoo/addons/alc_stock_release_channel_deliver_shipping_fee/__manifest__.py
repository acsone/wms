# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Stock Release Channel Deliver Shipping Fee",
    "description": """This module adds Alcyon shipping fee logic in case of
    ship picking validated in release channel auto process.""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        "alc_stock_release_channel_deliver",
        "alc_shipping_fee",
    ],
    "data": [],
    "demo": [],
}

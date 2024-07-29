# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Stock Release Channel Print Shipment Advice",
    "description": """This module allows users to print shipping advices generated
    from a release channel.""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        # fmt: off
        # OCA
        "stock_release_channel_shipment_advice_deliver",
        # fmt: on
    ],
    "data": ["views/stock_release_channel.xml"],
    "demo": [],
}

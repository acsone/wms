# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Stock Release Channel User Gls",
    "description": """
        This addon add an extra check for gls picking deliver""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        # fmt: off
        # Custom
        "alc_stock_release_channel_user",
        # OCA
        "delivery_carrier_label_gls",
        # fmt: on
    ],
    "data": [],
    "demo": [],
}

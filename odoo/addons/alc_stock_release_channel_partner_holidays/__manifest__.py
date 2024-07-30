# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Release Channel Partner Holidays",
    "description": """
        Allows to raise an error during channel picking assignation if the partner is on holidays""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        # Custom
        "alc_partner_holidays",
        # OCA
        "stock_release_channel_process_end_time",
    ],
}

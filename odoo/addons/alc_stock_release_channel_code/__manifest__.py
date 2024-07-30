# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Stock Release Channel Code",
    "description": """This module adds a channel_code field which replace the old
    round temlate code.""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        # OCA
        "stock_release_channel",
    ],
    "data": ["views/stock_release_channel_views.xml"],
    "demo": [],
}

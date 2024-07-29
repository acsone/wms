# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Stock Release Channel User",
    "description": """
        Alcyon: Manage Allowed operators on release channels""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # fmt: off
        # OCA
        "stock_release_channel",
        # fmt: on
    ],
    "data": ["views/stock_release_channel.xml"],
    "demo": [],
}

# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Stock Release Channel Tree",
    "description": """
        This addon replace release channels tree view""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        # Custom
        "alc_stock_release_channel_tag",
        # OCA
        "stock_release_channel_geoengine",
        "stock_release_channel_process_end_time",
    ],
    "data": ["views/stock_release_channel.xml"],
}

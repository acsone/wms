# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Stock Release Channel Preparation Plan",
    "description": """
        This addon define release channel preparation plan""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": ["stock_release_channel", "alc_stock_release_channel_menu"],
    "data": [
        "security/stock_release_channel_preparation_plan.xml",
        "views/stock_release_channel_preparation_plan.xml",
        "views/stock_release_channel.xml",
    ],
    "demo": ["demo/stock_release_channel_preparation_plan.xml"],
}

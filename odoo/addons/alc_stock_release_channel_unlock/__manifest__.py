# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Stock Release Channel Unlock",
    "description": """
        This addon adds a wizard to simplify release channels unlock""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        "alc_stock_release_channel_pick_allowed",
        "alc_stock_release_channel_tag",
        "alc_stock_release_channel_menu",
    ],
    "data": [
        "security/alc_stock_release_channel_unlock.xml",
        "wizards/alc_stock_release_channel_unlock.xml",
    ],
    "demo": [],
}

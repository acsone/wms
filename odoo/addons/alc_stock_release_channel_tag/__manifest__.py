# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Stock Release Channel Tag",
    "description": """
        This addon add tags to release channel and partner to help selecting picking to release""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        # Custom
        "alc_stock_release_channel_menu",
        # OCA
        "stock_release_channel",
        "stock_release_channel_geoengine",
    ],
    "data": [
        "security/alc_stock_release_channel_tag.xml",
        "views/stock_release_channel.xml",
        "views/res_partner.xml",
        "views/alc_stock_release_channel_tag.xml",
    ],
    "demo": ["demo/alc_stock_release_channel_tag.xml"],
}

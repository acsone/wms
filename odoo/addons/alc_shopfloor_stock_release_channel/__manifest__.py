# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Shopfloor stock release channel",
    "description": """
        add delivery round on current picking""",
    "version": "16.0.2.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "depends": [
        "shopfloor_batch_automatic_creation",
        "stock_release_channel",
        "alc_stock_release_channel_user",
        "alc_stock_release_channel_pick_allowed",
    ],
    "data": ["views/res_users.xml", "views/shopfloor_menu.xml"],
}

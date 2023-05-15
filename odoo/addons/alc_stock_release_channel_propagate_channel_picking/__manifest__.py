# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Stock Release Channel Propagate Channel Picking",
    "description": """
        Adds the propagation of release channel to pickings""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        "stock_release_channel_propagate_channel_picking",
    ],
    "post_init_hook": "post_init_hook",
}

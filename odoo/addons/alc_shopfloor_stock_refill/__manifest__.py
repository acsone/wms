# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Shopfloor Stock Refill",
    "description": """config module for content transfer scenario""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "depends": [
        # OCA
        "shopfloor",
    ],
    "post_init_hook": "post_init_hook",
}

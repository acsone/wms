# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Stock Release Channel Picking Batch Creation",
    "description": """
        This addon make the picking batch creation process consider user prefernces on release channels""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        # Custom
        "alc_stock_release_channel_pick_allowed",
        "alc_stock_release_channel_user",
        # OCA
        "stock_picking_batch_creation",
    ],
    "data": ["views/stock_picking_batch.xml", "wizards/make_picking_batch.xml"],
}

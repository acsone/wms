# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Alc Stock Release Channel Plan",
    "summary": """
        Add tags to preparation plan""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        # Custom
        "alc_stock_release_channel_menu",
        # OCA
        "stock_release_channel_plan",
    ],
    "data": ["wizards/launch_plan.xml"],
}

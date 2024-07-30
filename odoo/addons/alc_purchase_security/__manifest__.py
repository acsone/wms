# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Purchase Security",
    "description": """
        This addon customize purchase module security""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        # Others
        "purchase",
    ],
    "data": ["security/ir.model.access.csv", "views/ir_ui_menu.xml"],
    "demo": [],
}

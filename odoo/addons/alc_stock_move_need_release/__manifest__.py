# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Stock Move Need Release",
    "description": """
        This addon displays the need_release field in stock move form view for a
        restricted group of users. It also adds a server action to allow changing its value
        if needed""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": ["stock_available_to_promise_release"],
    "data": ["security/groups.xml", "views/stock_move.xml"],
    "demo": [],
}

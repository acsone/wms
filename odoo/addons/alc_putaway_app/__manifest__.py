# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Putaway App",
    "description": """
        Allows to collect all modules for putaway application""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "application": True,
    "depends": [
        "stock_available_to_promise_release",
        "stock_dynamic_routing",
    ],
}

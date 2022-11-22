# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Order Picking App",
    "description": """
        Order Picking App""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        "stock_available_to_promise_release",
        "stock_dynamic_routing",
        "stock_move_auto_assign_auto_release",
        "stock_picking_start",
        "stock_release_channel",
    ],
    "data": [],
    "demo": [],
    "application": True,
    "installable": True,
}

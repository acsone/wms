# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Delivery Rounds Operator",
    "description": """
        Alcyon: Manage Allowed operators on delivery rounds""",
    "version": "10.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": ["delivery_rounds", "stock_picking_assignment"],
    "data": ["views/round_instance.xml", "views/round_template.xml"],
    "demo": [],
}

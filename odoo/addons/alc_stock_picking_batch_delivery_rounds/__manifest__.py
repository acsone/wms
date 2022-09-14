# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Stock Picking Batch Delivery Rounds",
    "description": """Group pickings by delivery rounds""",
    "version": "10.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "depends": [
        "alc_delivery_rounds_operator",
        "alc_stock_picking_batch_creation",
        "delivery_rounds",
        "stock",
        "stock_location",
        "specific_stock",
        "stock_picking_batch_creation",
        "alc_stock_picking_batch_assignment",
        "alc_delivery_rounds_close_pickings_by_zone",
    ],
    "data": ["views/res_users.xml", "views/stock_picking_wave.xml"],
    "demo": [],
    'installable': False
}
# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Stock Picking Batch Creation",
    "description": """
        stock picking batch creation""",
    "version": "10.0.1.0.1",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "depends": [
        "stock_picking_batch_creation",
        "sale",
        "sale_stock",
        "stock_picking_assignment",
        "stock_picking_sequence",
    ],
    "data": [
        "data/devices.xml",
        "views/res_partner.xml",
        "views/stock_device_type.xml",
        "views/stock_picking_wave.xml",
    ],
    "demo": [],
    'installable': False
}
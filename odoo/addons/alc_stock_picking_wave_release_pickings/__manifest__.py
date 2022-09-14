# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Stock Picking Wave Release Pickings",
    "description": """
        When cancelling a wave of pickings, release the pickings to be attached again to another wave""",
    "version": "10.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "depends": ["stock_picking_wave", "alc_stock_picking_batch_assignment"],
    "data": ["views/stock_picking_wave.xml", "data/ir_config_parameter.xml"],
    "demo": [],
    'installable': False
}
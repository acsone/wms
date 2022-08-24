# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Delivery Rounds Close Pickings By Zone",
    "description": """
        Close/Open pickings by zone on delivery rounds""",
    "version": "10.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "depends": [
        "queue_job",
        "delivery_rounds",
        "delivery_rounds_alcyon",
        "stock_picking_zone",
        "stock_picking_assignment",
        "stock_picking_wave",
        "alc_stock_picking_batch_assignment",
        "alc_delivery_rounds_geooptimize",
    ],
    "data": ["views/round_template.xml", "views/round_instance.xml", "views/css.xml"],
    "demo": [],
}

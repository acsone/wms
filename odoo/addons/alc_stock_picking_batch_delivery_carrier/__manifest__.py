# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Stock Picking Batch Delivery Carrier",
    "description": """
        Take the carrier into account when creating a cluster picking""",
    "version": "10.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "depends": [
        "base_partition",
        "delivery_rounds",
        "delivery",
        "alc_stock_picking_batch_delivery_rounds",
    ],
    "data": ["wizards/make_picking_batch.xml"],
}

# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Stock Picking No Pack In Pack",
    "description": """
        Prevent pack in pack""",
    "version": "10.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "depends": [
        "stock_picking_subcode",
        "alc_delivery_carrier_gls",
        "alc_gls_putinpack",
        "delivery_rounds",
    ],
    "data": [],
    "demo": [],
    'installable': False
}
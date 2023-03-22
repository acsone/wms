# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Shopfloor Unassign Wave",
    "description": """
        override unassign wave method to release the pickings""",
    "version": "10.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "depends": [
        "alc_shopfloor",
        "alc_stock_picking_wave_release_pickings"  # TODO: has been removed
    ],
    "data": [],
    'installable': False
}
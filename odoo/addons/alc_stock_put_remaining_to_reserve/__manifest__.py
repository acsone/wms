# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Stock Put Remaining To Reserve",
    "description": """
        Put remaining quantities to reserve""",
    "version": "10.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "depends": [
        "alc_product_category_business_unit",
        "specific_stock",
        "stock",
        "stock_picking_zone",
        "stock_refill",
    ],
    "data": ["views/stock_picking.xml"],
    "demo": [],
}

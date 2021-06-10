# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
{
    "name": "Stock Picking Assignment",
    "version": "10.0.1.0.1",
    "category": "Stock Management",
    "author": "Sylvain Van Hoof",
    "description": """
    Stock Picking Assignment
    """,
    "depends": ["stock"],
    "data": [
        "views/stock_inventory.xml",
        "views/stock_scrap.xml",
        "views/stock_picking.xml",
    ],
    "installable": True,
    "license": "LGPL-3",
    "application": False,
}

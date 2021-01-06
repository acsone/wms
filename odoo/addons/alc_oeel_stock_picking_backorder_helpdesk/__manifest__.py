# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
{
    "name": "Alc Oeel Stock Picking Backorder Helpdesk",
    "description": """
        Alcyon: Add the ability to create a helpdesk ticket in case of backorder""",
    "version": "10.0.1.0.0",
    "license": "Other proprietary",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": ["alc_oeel_helpdesk", "stock_picking_backorder"],
    "data": [
        "wizards/stock_backorder_choice.xml",
        "views/stock_backorder_reason.xml",
        "data/stock_backorder_reason.xml",
    ],
    "demo": [],
}

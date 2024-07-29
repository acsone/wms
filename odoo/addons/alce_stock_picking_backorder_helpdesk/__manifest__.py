# Copyright 2021 ACSONE SA/NV
{
    "name": "Alc Oeel Stock Picking Backorder Helpdesk",
    "description": """
        Alcyon: Add the ability to create a helpdesk ticket in case of backorder""",
    "version": "16.0.1.0.0",
    "license": "Other proprietary",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # fmt: off
        # Custom
        "alc_stock_picking_backorder_reason",
        "alce_helpdesk",
        # fmt: on
    ],
    "data": [
        "wizards/stock_backorder_choice.xml",
        "views/stock_backorder_reason_views.xml",
        "data/stock_backorder_reason.xml",
    ],
    "demo": [],
    "installable": True,
}

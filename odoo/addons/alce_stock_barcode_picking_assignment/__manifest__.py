# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
{
    "name": "Alce Stock Barcode Picking Assignment",
    "description": """
        Alcyon: Add barcode command on picking assignment""",
    "version": "10.0.1.0.0",
    "license": "Other proprietary",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    # BE CAREFUL ALL the dependencies must BE LGPL or OEEL!!!
    # stock_barcode is an Odoo enterprise module
    "depends": ["stock_barcode", "stock_picking_assignment"],
    "data": ["views/stock_picking.xml"],
}

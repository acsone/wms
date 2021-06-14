# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Alc Stock Barcode Picking Type",
    "description": """
        Alcyon: Declare a default picking type on stock.location

        This picking type is used by the OEEL barcode app to create the right
        type of picking when a location is scanned.
        """,
    "version": "10.0.1.0.0",
    "license": "LGPL-3",  # MUST BE LGPL since will be mixed with barcode OEEL
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": ["stock"],
    "data": ["views/stock_location.xml"],
    "demo": [],
    "pre_init_hook": "pre_init_hook",
}

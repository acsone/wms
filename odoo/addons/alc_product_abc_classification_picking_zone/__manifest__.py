# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Product Abc Classification Picking Zone",
    "description": """
        Alcyon: Auto assign classification profile based on picking zone""",
    "version": "10.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        "alc_product_picking_zone",
        "product_abc_classification_base",
        "web_m2x_options",
    ],
    "data": ["views/picking_zone.xml", "views/abc_classification_profile.xml"],
    "demo": [],
}

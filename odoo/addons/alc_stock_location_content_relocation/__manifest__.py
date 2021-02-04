# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Stock Location Content Relocation",
    "description": """
        Wizard to move stocks from old to new locations""",
    "version": "10.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "depends": [
        "product",
        "stock",
        "stock_product_bin",
        "stock_picking_zone",
        "stock_storage_type",
        "stock_available",
    ],
    "data": ["wizards/alc_location_content_relocation_generator.xml"],
    "demo": [],
}

# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc stock picking number package",
    "description": """
        Compute the amount of packages a picking out should have depending on the wieght of the products and the limit fixed by the carrier""",
    "version": "10.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "depends": ["stock", "delivery", "delivery_rounds", "alc_product_dimensions"],
    "data": ["views/delivery_carrier.xml", "views/stock_picking.xml"],
    "demo": [],
}

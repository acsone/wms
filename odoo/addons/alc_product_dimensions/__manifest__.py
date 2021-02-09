# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Product Dimensions",
    "description": """
        compute product product diemnsions based on product template dimensions""",
    "version": "10.0.1.0.1",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "depends": ["product", "product_dimension"],
    "data": ["views/product_template.xml"],
    "demo": [],
    "pre_init_hook": "pre_init_hook",
}

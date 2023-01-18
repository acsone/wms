# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Pharmacy Product fields",
    "description": """Alcyon Pharmacy Product fields""",
    "version": "10.0.3.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        "alc_product_category_property",
        "specific_data",
        "product_manufacturer",
        "alc_product_category_data",
    ],
    "application": False,
    "data": ["views/product_template.xml", "views/product_product.xml"],
    "demo": [],
    'installable': False
}
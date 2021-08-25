# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc PIM",
    "description": """Alcyon PIM""",
    "version": "10.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        "pim",
        "alc_product_shop_category",
        # data dependencies
        "product_dimension",
        "stock_production_lot_expiry",
        "product_manufacturer",
        "specific_product",
        "specific_purchase",
        "alc_product_audit",
    ],
    "application": False,
    "data": [
        "data/attribute_group.xml",
        "data/attribute_set.xml",
        "data/product_category.xml",
        "data/attribute_attribute.xml",
    ],
    "demo": [],
}

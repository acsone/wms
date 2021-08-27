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
        "alc_pim_product",
        "alc_product_shop_category",
        "alc_product_link_notice",
        "product_animal_species",
        # data dependencies
        "product_dimension",
        "stock_production_lot_expiry",
        "product_manufacturer",
        "specific_product",
        "specific_purchase",
        "alc_product_audit",
        "product_brand",
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

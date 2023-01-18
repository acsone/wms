# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Reception Pharmacy",
    "description": """
        Alcyon: Manage reception of product from the Souverain pharmacy""",
    "version": "10.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    # TODO split delivery_rounds...
    "depends": [
        "alc_delivery_rounds_assign_blocking",
        "specific_data",
        "stock",
        "alc_product_category_data",
    ],
    "data": [
        "data/ir_sequence.xml",
        "data/product_product.xml",
        "views/reception_pharmacy.xml",
        "security/ir.model.access.csv",
    ],
    "demo": [],
    "external_dependencies": {"python": ["openupgradelib"]},
    "pre_init_hook": "pre_init_hook",
    "installable": False,
}

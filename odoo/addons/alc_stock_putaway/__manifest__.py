# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Stock Putaway",
    "description": """
        Alcyon: Manage stock putway

        This Addon is an APP and should not contains logic..
        """,
    "version": "10.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        "stock_storage_type",
        "stock_storage_type_putaway_abc",
        "alc_product_abc_classification",
        "product_abc_classification_sale_stock",
    ],
    "data": ["data/abc_classification_profile.xml"],
    "application": True,
}

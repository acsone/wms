# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Stock Storage Type Fixed Location",
    "description": """
        Glue module between stock_product_bin and stock_storage_type to
        support fixed locations into putaway sequence.

        Will be dropped in 14.0 since it's natively supported by
        stock_storage_type and the putaway rule of odoo
        """,
    "version": "10.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": ["stock_product_bin", "stock_storage_type"],
    'installable': False
}
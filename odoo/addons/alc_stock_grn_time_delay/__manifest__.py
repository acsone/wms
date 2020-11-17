# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Stock Grn Time Delay",
    "description": """
        Add information about outdated receipt based on the GRN date""",
    "version": "10",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "depends": ["stock", "stock_grn"],
    "data": ["views/stock_config_settings.xml", "views/stock_picking.xml"],
    "external_dependencies": {"python": ["numpy"]},
    "demo": [],
}

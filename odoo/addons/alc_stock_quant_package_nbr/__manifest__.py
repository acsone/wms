# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Stock Quant Package Nbr",
    "description": """
        Alcyon: Manage nbr packages/boxes used  for a stock quant package""",
    "version": "10.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": ["stock"],
    "data": ["views/stock_quant_package.xml"],
    "demo": [],
    "pre_init_hook": "pre_init_hook",
    'installable': False
}
# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Partner Manual Sale Order",
    "description": """
        Alcyon: Allows to specify if a partner can be selected from the UI to create a new sale order""",
    "version": "10.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": ["sale"],
    "data": ["views/res_partner.xml", "views/sale_order.xml"],
    "demo": [],
    "pre_init_hook": "pre_init_hook",
    "post_init_hook": "post_init_hook",
}

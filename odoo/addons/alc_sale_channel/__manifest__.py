# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Sale Channel",
    "description": """
        Alcyon: Add sale channel on sale order

        The sale_channel is useful to know the sale order origin
        """,
    "version": "10.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": ["sale", "sales_team"],
    "data": ["views/sale_order.xml"],
    "external_dependencies": {"python": ["openupgradelib"]},
    "pre_init_hook": "pre_init_hook",
    'installable': False
}
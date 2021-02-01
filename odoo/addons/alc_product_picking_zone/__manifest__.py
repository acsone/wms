# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Product Picking Zone",
    "description": """
        Alcyon: Display the default picking zone on the product form.

        The default picking zone is the one of the first route defined on the product
        """,
    "version": "10.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": ["stock_picking_zone"],
    "external_dependencies": {"python": ["openupgradelib"]},
    "data": ["views/product_template.xml"],
    "pre_init_hook": "pre_init_hook",
}

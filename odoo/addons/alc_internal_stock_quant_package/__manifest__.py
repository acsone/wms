# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Internal Stock Quant Package",
    "description": """
        Alcyon: Allows to declare internal stock quant package

        An internal stock quant package will never leave the warehouse. It's
        an package used in the picking process and is emptied when 'a put
        in pack' operation occurs or when the picking is validated (except
        if configured to not do it on the picking type).
        """,
    "version": "10.0.2.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": ["stock", "delivery"],
    "data": [
        "security/ir.model.access.csv",
        "views/stock_quant_package.xml",
        "views/stock_picking_type.xml",
    ],
    "demo": [],
    'installable': False
}
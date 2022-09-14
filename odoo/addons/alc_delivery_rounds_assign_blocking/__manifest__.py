# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Delivery Rounds Assign Blocking",
    "description": """
        Exclude pickings from delivery rounds if it is only backorders, or only human products, or only free products in the picking""",
    "version": "10.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "depends": ["base_partition", "delivery_rounds"],
    "data": ["views/sale_order.xml", "views/stock_picking.xml"],
    'installable': False
}
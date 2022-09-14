# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Alc Stock Picking Policy Block",
    "description": """
        Alcyon: Chek if the pickings with the same subcode are blocked
        depending on the picking_policy

        Pickings for the same procumrement group and the same subcode are blocked
        if the picking policy is 'all at once' and at least one of the picking into
        the group is not available.

        By default odoo blocks 'all at once' picking if not available. Into the
        Alcyon context, for a SO a picking 'PICK' is created by zone. (same subcode)
        If one of the pickings is not available in one zone we should block the
        others pickings.

        This addon add a field that can be used to detect such a cases
        """,
    "version": "10.0.1.0.0",
    "license": "LGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": ["stock", "stock_picking_subcode"],
    "data": [],
    "demo": [],
    'installable': False
}
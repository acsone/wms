# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Restocking Exclude Not Salable",
    "description": """
        a product that have been archived should not be suitable for restocking. A product that is no more sold is still suitable for restocking but the user should be warned. This is the purpose of this addon""",
    "version": "10",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "depends": ["sale", "stock", "specific_stock"],
    "data": ["wizards/stock_return_picking.xml", "views/product_archived_report.xml"],
    "demo": [],
}

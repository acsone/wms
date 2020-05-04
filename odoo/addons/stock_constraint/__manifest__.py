# -*- coding: utf-8 -*-
# Copyright 2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Stock Constraint",
    "version": "1.0",
    "author": "BCIM",
    "category": "Stock Management",
    "depends": ["stock", "stock_picking_subcode"],
    "data": ["security/res_groups.xml", "views/stock_picking.xml"],
    "installable": True,
    "auto_install": False,
    "license": "AGPL-3",
    "application": False,
}

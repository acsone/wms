# -*- coding: utf-8 -*-
# Copyright 2016-2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Procurement Sale",
    "version": "1.0",
    "author": "BCIM",
    "maintainer": "Camptocamp",
    "category": "Stock Management",
    "depends": ["procurement", "sale_stock", "stock_picking_subcode"],
    "data": ["views/stock_location_route.xml"],
    "installable": True,
    "auto_install": False,
    "license": "AGPL-3",
    "application": False,
}

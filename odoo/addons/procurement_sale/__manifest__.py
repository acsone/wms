# -*- coding: utf-8 -*-
# Copyright 2016-2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Procurement Sale",
    "version": "10.0.2.0.0",
    "author": "BCIM",
    "maintainer": "Camptocamp",
    "category": "Stock Management",
    "depends": [
        "alc_base_auto_join",
        "procurement",
        "sale_cancel_remaining",
        "sale_stock",
        "stock_available",
        "stock_picking_subcode",
        "web_readonly_bypass",
    ],
    "data": ["views/sale_order.xml", "views/stock_location_route.xml"],
    "installable": True,
    "auto_install": False,
    "license": "AGPL-3",
    "application": False,
}

# -*- coding: utf-8 -*-
# Copyright 2016-2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Procurement Sale",
    #####################################################################
    # split partially into alc_sale_qty_unavailable where the fields for
    # quantity unavailable are added
    #####################################################################
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
        "web_readonly_bypass",
    ],
    "data": ["views/sale_order.xml", "views/stock_location_route.xml"],
    "installable": False,
    "auto_install": False,
    "license": "AGPL-3",
    "application": False,
}

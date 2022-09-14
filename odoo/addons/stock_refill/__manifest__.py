# -*- coding: utf-8 -*-
# Copyright 2016-2017 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Stock Refill",
    "version": "10.0.1.0.1",
    "author": "BCIM",
    "maintainer": "Camptocamp",
    "category": "Stock Management",
    "depends": ["stock", "stock_quant_bylocation"],
    "data": [
        "wizards/stock_config_settings.xml",
        "views/stock_picking_type.xml",
        "views/stock_location.xml",
    ],
    "installable": False,
    "auto_install": False,
    "license": "AGPL-3",
    "application": False,
}

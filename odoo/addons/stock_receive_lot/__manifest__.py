# -*- coding: utf-8 -*-
# Copyright 2017-2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Stock Receive Wizard",
    "version": "10.0.1.0.0",
    "author": "BCIM",
    "maintainer": "Camptocamp",
    "license": "LGPL-3",  # MUST BE LGPL since will be mixed with helpdesk OEEL
    "category": "Stock Management",
    "depends": ["product_expiry", "stock", "stock_location_act_as_view"],  # LGPL
    "data": [
        "views/stock_location.xml",
        "views/stock_pack_operation.xml",
        "wizards/stock_pack_operation_lot_add.xml",
        "views/stock_picking.xml",
    ],
    "installable": True,
}

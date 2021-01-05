# -*- coding: utf-8 -*-
# Copyright 2017-2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Stock Receive Wizard",
    "version": "10.0.1.0.0",
    "author": "BCIM",
    "maintainer": "Camptocamp",
    "license": "AGPL-3",
    "category": "Stock Management",
    "depends": [
        "stock",
        "stock_location_act_as_view",
        "stock_picking_assignment",
        "stock_production_lot_expiry",
        "stock_production_lot_expired_dates",
        "web_widget_inputmask",
    ],
    "data": [
        "views/stock_location.xml",
        "views/stock_pack_operation.xml",
        "wizards/stock_pack_operation_lot_add.xml",
        "views/stock_picking.xml",
    ],
    "installable": True,
}

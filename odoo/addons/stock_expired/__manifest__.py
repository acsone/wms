# -*- coding: utf-8 -*-
# Copyright 2016 Julien Coux (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Stock expired",
    "version": "10.0.2.0.0",
    "author": "Camptocamp",
    "license": "AGPL-3",
    "category": "Warehouse",
    "depends": [
        "alc_base_auto_join",
        "mail",
        "product_expiry",
        "stock",
        "stock_production_lot_expiry",
    ],
    "website": "http://www.camptocamp.com",
    "data": [
        # Data
        "data/data.xml",
        # Views
        "views/stock_location.xml",
        "views/stock_quant.xml",
        "views/stock_picking.xml",
    ],
    "installable": True,
}

# -*- coding: utf-8 -*-
# Copyright 2016-2017 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Delivery Rounds Refill",
    "version": "10.0.1.1.0",
    "author": "BCIM",
    "category": "Stock Management",
    "depends": ["stock_refill", "delivery_rounds", "stock_barcode_fix"],
    "data": [
        "views/stock_quant.xml",
        "security/ir.model.access.csv",
        "views/report_stock_refill_arrange.xml",
        "views/report_stock_refill_reassort.xml",
        "views/round_instance.xml",
        "wizards/create_picking.xml",
    ],
    "installable": True,
    "auto_install": False,
    "license": "AGPL-3",
    "application": False,
}

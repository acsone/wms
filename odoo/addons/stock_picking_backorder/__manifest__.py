# -*- coding: utf-8 -*-
# Copyright 2016 Julien Coux (Camptocamp)
# Copyright 2016-2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

{
    "name": "Stock Picking Backorder",
    "version": "10.0.2.0.0",
    "author": "BCIM, Camptocamp",
    "license": "LGPL-3",  # MUST BE LGPL since will be mixed with helpdesk OEEL
    "category": "Warehouse",
    "depends": ["stock_grn", "stock_receive_lot"],  # requires LGPL
    "data": [
        "views/res_partner.xml",
        "views/stock_backorder_reason.xml",
        "views/stock_picking.xml",
        "wizards/stock_backorder_choice.xml",
        "security/ir.model.access.csv",
        "data/stock_backorder_reason.xml",
    ],
    "installable": True,
}

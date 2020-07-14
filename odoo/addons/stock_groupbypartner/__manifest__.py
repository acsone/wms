# -*- coding: utf-8 -*-
# Copyright 2016-2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Stock Group by partner",
    "version": "10.0.2.0.1",
    "author": "BCIM, ACSONE SA/NV",
    "maintainer": "Camptocamp",
    "category": "Stock Management",
    "depends": ["sale_stock", "stock_constraint", "delivery"],
    "data": [
        "views/procurement_group.xml",
        "views/stock_picking.xml",
        "views/stock_picking_type.xml",
    ],
    "installable": True,
    "auto_install": False,
    "license": "AGPL-3",
    "application": False,
}

# -*- coding: utf-8 -*-
# Copyright 2017 Julien Coux (Camptocamp)
# Copyright 2017 Sylvain Van Hoof (Okia SPRL)
# Copyright 2017-2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Product additional for Alcyon",
    "version": "10.0.1.0.0",
    "author": "Camptocamp",
    "license": "AGPL-3",
    "category": "Product",
    "depends": [
        "pricelist_discount",
        "product",
        "purchase",
        "sale",
        "sale_stock",
        "stock",
        "stock_available",
        "stock_constraint",
        "stock_picking_subcode",
        "stock_reassign_auto",
    ],
    "website": "http://www.camptocamp.com",
    "data": [
        # Views
        "views/product_template.xml",
        "views/product_supplierinfo.xml",
        "views/purchase_order.xml",
    ],
    "installable": True,
}

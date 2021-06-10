# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
{
    "name": "Stock Barcode Fix",
    "version": "10.0.1.0.0",
    "author": "BCIM",
    "category": "Stock Management",
    # BE CAREFUL ALL the dependencies must BE LGPL or OEEL!!!
    # stock_barcode is an Odoo enterprise module
    "depends": [
        "stock_barcode",
        "alce_stock_barcode_easy_operation",
        "alc_stock_barcode_picking_type",
    ],
    "installable": True,
    "auto_install": False,
    "license": "Other proprietary",
    "application": False,
    "pre_init_hook": "pre_init_hook",
}

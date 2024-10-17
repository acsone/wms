# Copyright 2021 ACSONE SA/NV
{
    "name": "Alce Stock Barcode",
    "version": "16.0.1.0.0",
    "author": "ACSONE SA/NV",
    "category": "Stock Management",
    # BE CAREFUL ALL the dependencies must BE LGPL or OEEL!!!
    # stock_barcode is an Odoo enterprise module
    "depends": [
        # Odoo Enterprise
        "stock_barcode",
        # Alcyon
        "alc_stock_barcode_picking_type",
        # Alcyon/Stock Management
        "alce_stock_barcode_easy_operation",
    ],
    "data": ["views/stock_picking_views.xml"],
    "installable": True,
    "license": "Other proprietary",
    "assets": {
        "web.assets_backend": [
            "alce_stock_barcode/static/src/js/*",
        ],
    },
}

# Copyright 2021 ACSONE SA/NV
{
    "name": "Alce Stock Barcode Picking Assignment",
    "description": """
        Alcyon: Add barcode command for picking assignment""",
    "version": "16.0.1.0.0",
    "license": "Other proprietary",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    # BE CAREFUL ALL the dependencies must BE LGPL or OEEL!!!
    # stock_barcode is an Odoo enterprise module
    "depends": [
        # Odoo Enterprise
        "stock_barcode",
        # Third-party
        "stock_picking_start",
        # Alcyon/Stock Management
        "alce_stock_barcode_easy_operation",
    ],
    "data": ["views/stock_picking_views.xml"],
    "installable": True,
}

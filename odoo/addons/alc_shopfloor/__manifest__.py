# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Shopfloor",
    "description": """
        Alcyon :Shopfloor Scan scenario""",
    "version": "10.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        "shopfloor_base",
        "stock",
        "stock_storage_type",
        "base_jsonify",
        "base_rest",
        "stock_picking_completion_info",
        "stock_quant_package_dimension",
        "product_packaging_type",
        "delivery",
        "product_expiry",
        "product_manufacturer",
        "stock_picking_assignment",
        "stock_picking_show_backorder",
        "stock_helper",
    ],
    "data": [
        "data/scenario_location_content_transfer.xml",
        "data/stock_picking_type_location_content_transfer.xml",
        "data/profile_location_content_transfer.xml",
        "data/menu_location_content_transfer.xml",
        "security/groups.xml",
        "views/shopfloor_menu.xml",
        "views/stock_location.xml",
        "views/stock_pack_operation.xml",
        "views/stock_picking_type.xml",
    ],
    "demo": ["demo/stock_picking_type_demo.xml", "demo/shopfloor_menu_demo.xml"],
}

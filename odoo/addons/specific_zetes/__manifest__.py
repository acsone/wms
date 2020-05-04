# -*- coding: utf-8 -*-
# © 2016 Sylvain Van Hoof
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Zetes integration for Alcyon",
    "version": "10.0.1.0.0",
    "author": "Sylvain Van Hoof",
    "license": "AGPL-3",
    "category": "Others",
    "description": """
    Zetes integration for Alcyon
    """,
    "depends": [
        "delivery_rounds",
        "delivery_rounds_refill",
        "stock",
        "specific_print",
        "specific_data",
        "stock_location",
        "stock_picking_assignment",
        "specific_stock",
        "stock_product_bin",
        "stock_barcode_fix",
        "stock_picking_fillwithstock",
        "stock_groupbypartner",
        "procurement_sale",
        "stock_picking_zone",
        "stock_lot_loss",
        "product_expiry",
    ],
    "data": [
        # Data
        "data/res_users.xml",
        # Views
        "views/res_users.xml",
        "views/res_partner.xml",
        "views/zetes_logger.xml",
        "views/stock_picking_type.xml",
        "views/stock_picking.xml",
        "views/stock_pack_operation_operator.xml",
        # Security
        "security/ir.model.access.csv",
        # Wizard
        "wizard/manage_uop.xml",
    ],
    "website": "http://www.camptocamp.com",
    "installable": True,
}

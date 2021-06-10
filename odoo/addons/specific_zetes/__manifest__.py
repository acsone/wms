# -*- coding: utf-8 -*-
# © 2016 Sylvain Van Hoof
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Zetes integration for Alcyon",
    "version": "10.0.2.0.0",
    "author": "Sylvain Van Hoof",
    "license": "AGPL-3",
    "category": "Others",
    "description": """
    Zetes integration for Alcyon
    """,
    "depends": [
        "alc_b2c_partner",
        "alc_delivery_rounds_operator",
        "alc_stock_barcode_picking_type",
        "delivery_rounds",
        "delivery_rounds_refill",
        "queue_job",
        "stock",
        "specific_print",
        "specific_data",
        "stock_location",
        "stock_picking_assignment",
        "specific_stock",
        "stock_product_bin",
        "stock_picking_fillwithstock",
        "stock_production_lot_expiry",
        "stock_groupbypartner",
        "procurement_sale",
        "stock_picking_zone",
        "stock_lot_loss",
        "product_expiry",
    ],
    "data": [
        "security/stock_pack_operation_deleted.xml",
        # Data
        "data/res_users.xml",
        "data/stock_pack_operation_deleted.xml",
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

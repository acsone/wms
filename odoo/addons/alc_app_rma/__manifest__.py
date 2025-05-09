# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc RMA App",
    "description": """
        Gather all rma related modules for Alcyon""",
    "version": "16.0.1.0.2",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "application": True,
    "depends": [
        # Third-party
        "product_warranty",
        "rma",
        "rma_delivery",
        "rma_delivery_procurement_group_carrier",
        "rma_lot",
        "rma_reason",
        "rma_sale",
        "rma_sale_lot",
        "rma_sale_reason",
        # Alcyon
        "alc_rma_activity",
        "alc_rma_operation_return_location",
        "alc_rma_original_picking_responsible",
        "alc_rma_report_delivery_slip",
        "alc_rma_sale_stock_restocking_fee_invoicing",
        "alc_rma_shipment_advice",
        "alc_rma_stock_delivery_slip",
        "alc_stock_picking_return_security",
    ],
}

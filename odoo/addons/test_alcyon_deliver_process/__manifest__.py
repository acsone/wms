# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Test Alcyon Deliver Porcess",
    "description": """Test Alcyon Deliver Porcess""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        # Custom
        "alc_additional_product_stock",
        "alc_cash_on_delivery",
        "alc_product_expiry",
        "alc_stock_delivery_slip",
        "alc_stock_lot_available",
        "alc_stock_picking_cancel_permission",
        "alc_stock_picking_cancel_permission",
        "alc_stock_release_channel_print_cash_on_delivery",
        # OCA
        "shipment_advice",
        "stock_move_auto_assign_auto_release",
        "stock_move_line_change_lot",
        "stock_picking_backorder_reason",
        "stock_picking_group_by_partner_by_carrier",
        "stock_picking_group_by_partner_by_carrier_by_customer",
        "stock_picking_start",
        "stock_release_channel_auto_release",
        "stock_release_channel_delivery",
        "stock_release_channel_process_end_time",
        "stock_release_channel_propagate_channel_picking",
        "stock_release_channel_propagate_channel_picking",
        "stock_release_channel_shipment_advice_deliver",
        # Others
        "product_expiry",
    ],
    "data": [],
    "demo": [],
}

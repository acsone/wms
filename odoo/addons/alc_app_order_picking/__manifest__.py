# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Order Picking App",
    "description": """
        Gather all order picking related modules for Alcyon""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        "alc_delivery_carrier_gls",
        "alc_partner_carrier",
        "base_delivery_carrier_label",
        "delivery_carrier_max_weight_constraint",
        "delivery_package_type_number_parcels",
        "product_total_weight_from_packaging",
        "shipment_advice",
        "stock_dynamic_routing",
        "stock_move_common_dest",
        "stock_picking_completion_info",
        "stock_picking_delivery_link",
        "stock_picking_start",
        "stock_picking_type_shipping_policy",
        "stock_production_lot_expired_date",
        "stock_production_lot_expiry",
        "stock_release_channel_auto_release",
        "stock_release_channel",
    ],
    "data": [],
    "demo": [],
    "application": True,
    "installable": True,
}

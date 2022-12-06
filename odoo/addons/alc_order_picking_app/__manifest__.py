# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Order Picking App",
    "description": """
        Order Picking App""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        "base_delivery_carrier_label",
        "product_total_weight_from_packaging",
        "stock_dynamic_routing",
        "stock_move_common_dest",
        "stock_picking_completion_info",
        "stock_picking_start",
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

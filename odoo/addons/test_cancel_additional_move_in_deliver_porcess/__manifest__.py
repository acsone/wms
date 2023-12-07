# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Test Cancel Additional Move In Deliver Porcess",
    "description": """
        This addon add tests to make sur deliver is correctlly done where there are additinal moves to cancel""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        "alc_additional_product_stock",
        "alc_stock_picking_cancel_permission",
        "alc_stock_release_channel_deliver",
        "stock_release_channel_auto_release",
        "stock_move_auto_assign_auto_release",
        "stock_release_channel_propagate_channel_picking",
        "stock_picking_group_by_partner_by_carrier",
        "stock_picking_group_by_partner_by_carrier_by_customer",
        "alc_stock_picking_cancel_permission",
    ],
    "data": [],
    "demo": [],
}

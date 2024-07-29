# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Stock Release Channel Dashboard",
    "description": """
        This addon improves release channels kanban view""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        # fmt: off
        # Custom
        "alc_report_delivery_slip",
        "alc_stock_release_channel_deliver_toursolver",
        "alc_stock_release_channel_pick_allowed",
        "alc_stock_release_channel_print_cash_on_delivery",
        "alc_stock_release_channel_print_shipment_advice",
        "alc_stock_release_channel_tag",
        "alc_stock_release_channel_weight",
        # OCA
        "stock_release_channel_auto_release",
        "stock_release_channel_geoengine",
        "stock_release_channel_process_end_time",
        "stock_release_channel_shipment_advice",
        "stock_release_channel_shipment_advice_deliver",
        # fmt: on
    ],
    "data": ["views/stock_picking.xml", "views/stock_release_channel.xml"],
    "assets": {
        "web.assets_backend": [
            "alc_stock_release_channel_dashboard/static/src/scss/channel_dashboard.scss",
            "alc_stock_release_channel_dashboard/static/src/views/**/*.js",
            "alc_stock_release_channel_dashboard/static/src/views/**/*.xml",
        ],
    },
}

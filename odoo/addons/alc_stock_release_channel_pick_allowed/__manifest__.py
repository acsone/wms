# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Stock Release Channel Pick Allowed",
    "description": """
        This addon adds a flag to release channels to define if the picking preparation
         is allowed or not. it also allows the definition per picking type.""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        # fmt: off
        # Custom
        "alc_stock_release_channel_menu",
        "alc_stock_release_channel_shipment_advice_toursolver",
        # OCA
        "queue_job",
        "queue_job_cron",
        "stock_picking_start",
        "stock_release_channel",
        # fmt: on
    ],
    "data": [
        "security/stock_release_channel_pick_allowed_log.xml",
        "views/stock_release_channel_pick_allowed_log.xml",
        "data/ir_cron.xml",
        "data/queue_job_function.xml",
        "views/stock_release_channel.xml",
        "views/stock_picking_type.xml",
    ],
    "demo": [],
}

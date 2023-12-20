# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Stock Release Channel Deliver",
    "description": """This module adds an action to the release channel to
    automate the delivery of its shippings.""",
    "version": "16.0.1.0.1",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        "stock_release_channel",
        "queue_job",
        "shipment_advice_planner_toursolver_queue_job",
        "stock_release_channel_shipment_advice",
        "web_notify",
        "stock_release_channel_process_end_time",
        "stock_picking_start",
        "stock_available_to_promise_release",
        "stock_release_channel_propagate_channel_picking",
        "alc_queue_job_background_channel",
    ],
    "data": [
        "security/stock_release_channel_deliver_check_wizard.xml",
        "wizards/stock_release_channel_deliver_check_wizard.xml",
        "data/queue_job_channel.xml",
        "data/queue_job_function.xml",
        "views/stock_release_channel.xml",
    ],
    "demo": [],
}

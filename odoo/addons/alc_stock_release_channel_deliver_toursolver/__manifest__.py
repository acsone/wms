# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Stock Release Channel Deliver Toursolver",
    "description": """Extends the release channel auto-deliver process to support
    toursolver shipping method.""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        # fmt: off
        # OCA
        "shipment_advice_planner_toursolver_queue_job",
        "stock_release_channel_shipment_advice_deliver",
        "stock_release_channel_shipment_advice_toursolver",
        # fmt: on
    ],
    "data": [
        "data/queue_job_function.xml",
        "views/stock_release_channel_views.xml",
    ],
    "demo": [],
}

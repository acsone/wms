# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Report Shipment Advice",
    "summary": """
        Shipment advice reporting for Alcyon""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        "stock_release_channel_shipment_advice",
        "shipment_advice_planner_toursolver",
        "alc_report_base",
        "shopfloor",
    ],
    "data": [
        "data/paperformat.xml",
        "views/report_shipment_advice.xml",
        # "views/stock_release_channel_views.xml",
    ],
    "demo": [],
    "installable": True,
}

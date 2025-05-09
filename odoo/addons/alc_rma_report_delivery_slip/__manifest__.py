# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc RMA Report Delivery Slip",
    "summary": """Adds RMA information on the delivery slip report""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # Third-party
        "rma_reason",
        # Alcyon
        "alc_report_delivery_slip",
    ],
    "assets": {
        "web.report_assets_common": [
            "alc_rma_report_delivery_slip/static/src/css/alc_rma_report_delivery_slip.css",
        ],
    },
    "data": ["views/report_delivery_slip.xml"],
    "demo": [],
    "installable": True,
}

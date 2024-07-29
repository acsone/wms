# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Data App",
    "description": """
        Gather all data related modules for Alcyon""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "application": True,
    "depends": [
        # fmt: off
        # Custom
        "alc_report_base",
        "alc_report_delivery_slip",
        "alc_report_invoice",
        "alc_report_purchase",
        "alc_report_sale",
        "alc_report_shipment_advice",
        "alc_report_stock_picking_operations",
        # fmt: on
    ],
}

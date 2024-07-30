# Copyright 2021 ACSONE SA/NV

{
    "name": "Alc All Enterprise",
    "description": """
        Alcyon addons under Odoo Enterprise licence""",
    "version": "16.0.2.15.7",
    "license": "Other proprietary",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # fmt: off
        # Custom
        "alce_account_followup_report",
        "alce_account_intrastat_category",
        "alce_account_intrastat_weight",
        "alce_account_reports_followup_data",
        "alce_helpdesk",
        "alce_report_intrastat_infos",
        "alce_split_coda",
        "alce_stock_barcode",
        "alce_stock_picking_backorder_helpdesk",
        # fmt: on
    ],
    "data": [],
    "demo": [],
    "application": True,
    "installable": True,
}

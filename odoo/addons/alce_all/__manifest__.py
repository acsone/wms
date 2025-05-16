# Copyright 2021 ACSONE SA/NV

{
    "name": "Alc All Enterprise",
    "description": """
        Alcyon addons under Odoo Enterprise licence""",
    "version": "16.0.2.23.14",
    "license": "Other proprietary",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # Alcyon
        "alce_account_followup_report",
        "alce_account_intrastat_category",
        "alce_account_intrastat_weight",
        "alce_account_move_line_search",
        "alce_report_intrastat_infos",
        "alce_stock_picking_backorder_helpdesk",
        # Alcyon/Accounting
        "alce_split_coda",
        # Alcyon/Helpdesk
        "alce_helpdesk",
        # Alcyon/Others
        "alce_account_reports_followup_data",
        # Alcyon/Stock Management
        "alce_stock_barcode",
    ],
    "data": [],
    "demo": [],
    "application": True,
    "installable": True,
}

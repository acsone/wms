# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Invoices Audit",
    "description": """
        Add custom filters for invoicing""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "depends": [
        # fmt: off
        # Custom
        "alc_partner_call_name",
        # OCA
        "partner_invoicing_mode_fourteen_days",
        "partner_invoicing_mode_monthly",
        "partner_invoicing_mode_ten_days",
        # fmt: on
    ],
    "data": ["views/account_move_views.xml"],
    "demo": [],
    "installable": True,
}

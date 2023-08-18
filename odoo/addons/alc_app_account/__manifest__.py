# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc App Account",
    "description": """Gather all account related modules for Alcyon""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        # Odoo
        "account",
        # OCA
        "account_invoice_merge",
        "account_invoice_check_total",
        "partner_invoicing_mode",
        "partner_invoicing_mode_at_shipping",
        "partner_invoicing_mode_monthly",
        # ALC
        "alc_account_security",
    ],
}

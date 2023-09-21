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
        "account_invoice_line_default_account",
        "account_invoice_check_total",
        "account_move_sent_usability",
        "account_reversal",
        "l10n_be_antibiotic_tax",
        "l10n_be_apb_tax",
        "l10n_be_eco_tax",
        "account_payment_mode_auto_reconcile",
        "mis_builder",
        "mis_builder_budget",
        "partner_invoicing_mode",
        "partner_invoicing_mode_at_shipping",
        "partner_invoicing_mode_fourteen_days",
        "partner_invoicing_mode_monthly",
        "partner_invoicing_mode_ten_days",
        "account_cutoff_picking",
        "account_invoice_accrual",
        "l10n_be_iso20022_pain",
        # ALC
        "account_invoice_sent",
        "alc_account_security",
        "alc_account_tax_precision",
        "alc_partner_invoicing_mode_default",
        "alc_account_invoice_accrual",
        "alc_account_cutoff_picking",
        "alc_account_payment_globalization",
    ],
}

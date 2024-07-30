# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Invoicing App",
    "description": """
        Gather all Invoicing related modules for Alcyon""",
    "version": "16.0.1.0.1",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "application": True,
    "depends": [
        # Custom
        "alc_account_invoice_cancel_permissions",
        "alc_account_move_default_reference_type",
        "alc_invoices_audit",
        "alc_ir_sequence_period",
        "alc_sale_invoicing_on_transfer",
        # OCA
        "account_banking_mandate",
        "account_banking_pain_base",
        "account_banking_sepa_direct_debit",
        "account_einvoice_generate",
        "account_invoice_export_ubl",
        "account_invoice_split_refund",
        "account_invoice_tax_required",
        "account_invoice_ubl",
        "account_payment_mode",
        "account_payment_partner",
        "account_payment_sale",
        "account_tax_one_vat",
        "account_tax_one_vat_purchase",
        "account_tax_one_vat_sale",
        "account_tax_unece",
        "base_business_document_import",
        "base_ubl",
        "base_ubl_payment",
        "base_ubl_payment_mode_required",
        "base_unece",
        "l10n_be_account_einvoice_generate",
        "pdf_helper",
        "purchase_invoicing_no_zero_line",
        "report_xml",
    ],
}

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
        # OCA/bank-payment
        "account_payment_mode",
        "account_payment_sale",
        "account_payment_partner",
        "account_banking_pain_base",
        "account_banking_mandate",
        "account_banking_sepa_direct_debit",
        # OCA/account-invoicing
        "account_tax_one_vat",
        "account_tax_one_vat_purchase",
        "account_tax_one_vat_sale",
        "account_invoice_tax_required",
        "account_invoice_split_refund",
        "purchase_invoicing_no_zero_line",
        # OCA/reporting-engine
        "report_xml",
        # OCA/community-data-files
        "base_unece",
        "account_tax_unece",
        # OCA/edi
        "base_ubl",
        "base_business_document_import",
        "pdf_helper",
        "account_einvoice_generate",
        "account_invoice_ubl",
        "base_ubl_payment",
        # edido-eu/peppol
        "account_invoice_export_ubl",
        "base_ubl_payment_mode_required",
        "l10n_be_account_einvoice_generate",
        # ALC
        "alc_cash_on_delivery",
        "alc_account_invoice_cancel_permissions",
        "alc_sale_invoicing_on_transfer",
        "alc_invoices_audit",
        "alc_ir_sequence_period",
    ],
}

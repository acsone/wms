# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Report Invoice",
    "summary": """
        Invoice reporting for Alcyon""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # fmt: off
        # Custom
        "alc_accounting_data",
        "alc_company_term_condition",
        "alc_report_base",
        "alc_report_intrastat_infos",
        # OCA
        "account_invoice_triple_discount",
        "account_payment_mode",
        "account_payment_partner",
        "l10n_be_apb_tax",
        "partner_fax",
        "sale_triple_discount",
        # Others
        "account",
        "sale",
        # fmt: on
    ],
    "data": [
        "views/account_payment_mode_views.xml",
        "views/report_invoice.xml",
        "views/res_partner.xml",
    ],
    "demo": [],
    "installable": True,
}

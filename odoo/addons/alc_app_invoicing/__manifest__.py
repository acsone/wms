# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Invoicing App",
    "description": """
        Gather all Invoicing related modules for Alcyon""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "application": True,
    "depends": [
        "account_tax_one_vat",
        "account_tax_one_vat_purchase",
        "account_tax_one_vat_sale",
        "account_invoice_tax_required",
        "alc_cash_on_delivery",
    ],
}

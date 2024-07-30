# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Madatory Supplier Invoice Number in Invoice/Refund",
    "version": "16.0.1.0.0",
    "summary": "Checks that supplier invoice number is given",
    "author": "ACSONE SA/NV",
    "license": "AGPL-3",
    "category": "Accounting & Finance",
    "depends": [
        # OCA
        "account_invoice_supplier_ref_unique",
    ],
    "data": ["views/res_config_settings.xml"],
    "installable": True,
}

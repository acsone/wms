# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Automatic Account Move Line Reconcile",
    "description": """
        Reconcile invoices and refunds taking the payment mode into account""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "depends": [
        # fmt: off
        # OCA
        "account_payment_partner",
        # Others
        "account",
        # fmt: on
    ],
    "data": [],
    "demo": [],
}
